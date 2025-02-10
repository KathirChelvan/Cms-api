fetch("http://127.0.0.1:5000/predict")
    .then(response => response.json())
    .then(data => {
        let tableBody = document.getElementById("table-body");
        Object.keys(data).forEach(drug => {
            data[drug].years.forEach((year, index) => {
                let row = document.createElement("tr");
                row.innerHTML = `
                    <td>${drug}</td>
                    <td>${year}</td>
                    <td>$${data[drug].total_spending[index].toFixed(2)}</td>
                    <td>$${data[drug].avg_spending[index].toFixed(2)}</td>
                `;
                tableBody.appendChild(row);
            });
        });
    })
    .catch(error => console.error("Error fetching predictions:", error));
