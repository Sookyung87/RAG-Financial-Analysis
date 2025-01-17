document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('stockQueryForm');
    const submitBtn = document.getElementById('submitBtn');
    const spinner = submitBtn.querySelector('.spinner-border');
    const errorMessage = document.getElementById('errorMessage');
    const resultArea = document.getElementById('resultArea');
    const resultTable = document.getElementById('resultTable');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Reset UI states
        errorMessage.classList.add('d-none');
        resultArea.classList.add('d-none');
        spinner.classList.remove('d-none');
        submitBtn.disabled = true;

        const formData = {
            user_id: document.getElementById('userId').value,
            password: document.getElementById('password').value,
            message: document.getElementById('query').value
        };

        try {
            const response = await fetch('/query_stock', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (data.success) {
                displayResults(data.data);
            } else {
                throw new Error(data.error || 'Failed to fetch stock information');
            }
        } catch (error) {
            if (error instanceof Error) {
                errorMessage.textContent = error.message;
            } else {
                errorMessage.textContent = "API 서버에 연결할 수 없습니다. API 서버가 실행 중인지 확인해주세요.";
            }
            errorMessage.classList.remove('d-none');
        } finally {
            spinner.classList.add('d-none');
            submitBtn.disabled = false;
        }
    });
    function displayResults(data) {
        resultTable.innerHTML = '';
        
        Object.entries(data).forEach(([key, value]) => {
            const row = document.createElement('tr');
    
            // value를 문자열로 변환한 후 처리
            const formattedValue = (typeof value === 'string' ? value : String(value))
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // 볼드체 처리
                .replace(/\n/g, '<br>');  // 줄바꿈 처리
    
            row.innerHTML = `
                <td class="fw-bold">${key}</td>
                <td>${formattedValue}</td>
            `;
            resultTable.appendChild(row);
        });
    
        resultArea.classList.remove('d-none');
    }
});
