package com.example.normalization

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AccountCircle
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.text.input.TextFieldValue
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.filled.Search
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.tooling.preview.Preview
import androidx.room.util.query
import kotlinx.coroutines.launch
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Body
import retrofit2.http.POST
import retrofit2.Call
import retrofit2.http.GET
import retrofit2.http.Path
import kotlin.coroutines.resume
import kotlin.coroutines.suspendCoroutine

data class QuestionRequest(val question: String)
data class ResponseData(val answer: String)

interface ChatApi {
    @POST("http://comjsh.store/rag") // 서버의 엔드포인트 (http://comjsh.store/rag)
    fun sendQuestion(@Body request: QuestionRequest): Call<ResponseData>
}



object RetrofitInstance {
    private const val BASE_URL = "http://comjsh.store/"

    val api: ChatApi by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ChatApi::class.java)
    }
}


suspend fun sendQuestionToServer(question: String): String {
    return try {
        val response = RetrofitInstance.api.sendQuestion(QuestionRequest(question)).execute()
        if (response.isSuccessful) {
            response.body()?.answer ?: "응답을 받을 수 없습니다."
        } else {
            "서버 오류: ${response.code()}"
        }
    } catch (e: Exception) {
        "네트워크 오류: ${e.localizedMessage}"
    }
}



class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MainScreen()
        }
    }
}

@Composable
fun MainScreen() {
    var selectedTab by remember { mutableStateOf(0) } // 현재 선택된 탭 인덱스 관리
    val tabTitles = listOf("질문하기", "임베딩 모델 변경", "마이페이지") // 탭 제목 목록

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFFF5F5F5)), // 배경색
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // 상단 앱바
        TopAppBar()

        // 탭 네비게이션
        TabRow(selectedTabIndex = selectedTab) {
            tabTitles.forEachIndexed { index, title ->
                Tab(
                    selected = selectedTab == index,
                    onClick = { selectedTab = index },
                    text = { Text(title) }
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // 선택된 탭에 따라 다른 화면을 보여줌
        when (selectedTab) {
            0 -> QuestionScreen()
            1 -> EmbeddingModelScreen()
            2 -> MyPageScreen()
        }
    }
}

// ✅ 상단 바
@Composable
fun TopAppBar() {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = "LLMJSH",
            fontSize = 20.sp,
            fontWeight = FontWeight.Bold,
            color = Color.Black
        )
        Spacer(modifier = Modifier.weight(1f)) // 오른쪽 정렬을 위한 Spacer

        IconButton(onClick = { /* TODO: 메뉴 버튼 클릭 시 동작 추가 */ }) {
            Icon(
                imageVector = Icons.Default.AccountCircle, // 기본 사용자 아이콘
                contentDescription = "더보기"
            )
        }
    }
}

@Composable
fun QuestionScreen() {
    var query by remember { mutableStateOf(TextFieldValue("")) } // 검색어 상태 저장
    var results by remember { mutableStateOf<List<Pair<String, String>>>(emptyList()) } // 대화 내역
    val listState = rememberLazyListState() // LazyColumn의 스크롤 상태


    // ✅ 새로운 메시지가 추가될 때 자동 스크롤
    LaunchedEffect(results.size) {
        if (results.isNotEmpty()) {
            listState.animateScrollToItem(results.size - 1)
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Spacer(modifier = Modifier.height(20.dp))

        Text(
            text = "무엇이 궁금하신가요?",
            fontSize = 25.sp,
            fontWeight = FontWeight.Bold
        )

        Spacer(modifier = Modifier.height(10.dp))

        Text(
            text = "RAG 기술이 적용된 LLM을 통해\n정확한 답변을 얻어보세요!",
            textAlign = TextAlign.Center,
            fontSize = 16.sp,
            color = Color.DarkGray
        )

        Spacer(modifier = Modifier.height(20.dp))

        // ✅ 대화창 (LazyColumn 사용)
        LazyColumn(
            state = listState,
            modifier = Modifier
                .fillMaxWidth()
                .weight(1f) // 남은 공간을 전부 차지
                .padding(8.dp),
            reverseLayout = false // 가장 최근 메시지가 아래쪽에 배치됨
        ) {
            items(results) { (question, answer) ->
                ChatBubble(text = question, isUser = true)  // 사용자 질문
                ChatBubble(text = answer, isUser = false)  // AI 응답
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        // ✅ 검색창
        SearchBar(query, onQuerySubmitted = { newQuery ->
            query = TextFieldValue("") // 입력창 초기화
            val response = "응답: \"$newQuery\"에 대한 답변입니다."
            results = results + listOf(Pair(newQuery, response)) // ✅ 새 대화 추가



        })
    }
}


@Composable
fun SearchBar(query: TextFieldValue, onQuerySubmitted: (String) -> Unit) {
    var textState by remember { mutableStateOf(query) }
    val coroutineScope = rememberCoroutineScope() // ✅ CoroutineScope 추가

    Box(
        modifier = Modifier
            .fillMaxWidth(0.9f)
            .height(50.dp)
            .background(Color.White, RoundedCornerShape(12.dp)),
        contentAlignment = Alignment.Center
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            TextField(
                value = textState.text,
                onValueChange = { textState = TextFieldValue(it) },
                keyboardOptions = KeyboardOptions(imeAction = ImeAction.Done),
                keyboardActions = KeyboardActions(
                    onDone = {
                        if (textState.text.isNotBlank()) {
                            val userQuery = textState.text
                            textState = TextFieldValue("") // ✅ 입력창 초기화

                            // ✅ 네트워크 요청을 비동기로 실행
                            coroutineScope.launch {
                                val response = sendQuestionToServer(userQuery)
                                onQuerySubmitted(response) // ✅ UI에 반영
                            }
                        }
                    }
                ),
                singleLine = true,
                modifier = Modifier.weight(1f),
                colors = TextFieldDefaults.colors(
                    focusedContainerColor = Color.White,
                    unfocusedContainerColor = Color.White,
                    disabledContainerColor = Color.Gray,
                    focusedIndicatorColor = Color.Transparent,
                    unfocusedIndicatorColor = Color.Transparent
                )
            )
            Icon(imageVector = Icons.Default.Search, contentDescription = "검색")
        }
    }
}





@Composable
fun ChatBubble(text: String, isUser: Boolean) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp),
        horizontalArrangement = if (isUser) Arrangement.End else Arrangement.Start
    ) {
        Box(
            modifier = Modifier
                .background(
                    color = if (isUser) Color.LightGray else Color.White,
                    shape = RoundedCornerShape(12.dp)
                )
                .padding(12.dp)
                .widthIn(min = 80.dp, max = 250.dp)
        ) {
            Text(text = text, fontSize = 16.sp, color = Color.Black)
        }
    }
}


// ✅ "임베딩 모델 변경" 화면
@Composable
fun EmbeddingModelScreen() {
    Column(
        modifier = Modifier.fillMaxSize().padding(16.dp)
    ) {
        Text("임베딩 모델 변경", fontSize = 24.sp, fontWeight = FontWeight.Bold)
        Spacer(modifier = Modifier.height(16.dp))

        // 체크박스 예제 (선택 가능한 모델 목록)
        var checked1 by remember { mutableStateOf(false) }
        var checked2 by remember { mutableStateOf(false) }

        Row(verticalAlignment = Alignment.CenterVertically) {
            Checkbox(checked = checked1, onCheckedChange = { checked1 = it })
            Text("KF-DeBERTa")
        }

        Row(verticalAlignment = Alignment.CenterVertically) {
            Checkbox(checked = checked2, onCheckedChange = { checked2 = it })
            Text("test-embedding-3-small")
        }
    }
}

// ✅ "마이페이지" 화면
@Composable
fun MyPageScreen() {
    Column(
        modifier = Modifier.fillMaxSize().padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text("마이페이지", fontSize = 24.sp, fontWeight = FontWeight.Bold)
        Spacer(modifier = Modifier.height(16.dp))

        // 사용자 프로필 정보
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = MaterialTheme.shapes.medium
        ) {
            Column(
                modifier = Modifier.padding(16.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                // 프로필 아이콘
                Icon(
                    imageVector = Icons.Default.AccountCircle,
                    contentDescription = "프로필 아이콘",
                    modifier = Modifier.size(60.dp)
                )

                Spacer(modifier = Modifier.height(8.dp))

                // 이메일 정보
                Text("user@gmail.com 변경 가능합니다", fontSize = 16.sp)
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // 설정 목록
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = MaterialTheme.shapes.medium
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("내 정보", fontSize = 16.sp)
                Spacer(modifier = Modifier.height(8.dp))
                Text("버전 v1.1")
                Spacer(modifier = Modifier.height(8.dp))
                Text("대화 기록 보기")
            }
        }
    }
}

// ✅ Preview (미리보기 기능)
@Preview(showBackground = true)
@Composable
fun PreviewMainScreen() {
    MainScreen()
}
