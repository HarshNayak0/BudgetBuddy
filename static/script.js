document.addEventListener('DOMContentLoaded', () => {

    // First chart: Budget Data
    const hiddenInput = document.getElementById('hiddenDataset').value;
    const roughDataset = JSON.parse(hiddenInput);
    
    const backgroundColors = getRandomColors(roughDataset.length);


    const dataset = roughDataset.map(item => ({
        category: item.category,
        allocated_amount: item.category === null ? 0 : item.allocated_amount
    }));

    const budgetData = {
        labels: dataset.map(item => item.category),
        datasets: [{
            data: dataset.map(item => item.allocated_amount),
            backgroundColor: backgroundColors
        }]
    };

    const budgetDataCtx = document.getElementById('budgetDataChart').getContext('2d');
    new Chart(budgetDataCtx, {
        type: 'pie',
        data: budgetData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: false,
                },
                legend: {
                    display: false,
                }
            }
        }
    });

    // Second chart: Comparing with Expenses
    const hiddenExpenseDataset = document.getElementById('compareExpenseHidden').value;
    const roughExpenseDataset = JSON.parse(hiddenExpenseDataset);
    

    const expenseDataset = roughExpenseDataset.map(item => ({
        category: item.category,
        amount: item.category === null ? 0 : item.amount
    }));

    const expenseData = {
        labels: expenseDataset.map(item => item.category),
        datasets: [{
            data: expenseDataset.map(item => item.amount),
            backgroundColor: backgroundColors
        }]
    };

    const expenseDataCtx = document.getElementById('expenseDataChart').getContext('2d');
    new Chart(expenseDataCtx, {
        type: 'pie',
        data: expenseData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: false,
                },
                legend: {
                    display: false,
                }
            }
        }
    });

    // Additional functions
    function getRandomColors(count) {
        const colors = [];
        for (let i = 0; i < count; i++) {
            const randomColor = getRandomColor();
            colors.push(randomColor);
        }
        return colors;
    }

    function getRandomColor() {
        const letters = '0123456789ABCDEF';
        let color = '#';
        for (let i = 0; i < 6; i++) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    }

});
