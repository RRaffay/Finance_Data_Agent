$(document).ready(function () {
    $('#chartViewerModal').on('shown.bs.modal', function () {
        fetchCharts();
    });

    $('#refresh-charts').on('click', function () {
        fetchCharts();
    });

    $('#download-chart').on('click', function () {
        const downloadUrl = $('#selected-chart').attr('src');
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = $('#selected-chart-label').text();
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });

    function fetchCharts() {
        $.get('/images', function (data) {
            const chartsContainer = $('#charts-container');
            chartsContainer.empty();
            data.forEach(function (image) {
                const imageUrl = '/images/' + image;
                const imgElement = $('<img>')
                    .attr('src', imageUrl)
                    .addClass('img-fluid m-2 chart-thumbnail')
                    .css('max-width', '200px')
                    .on('click', function () {
                        selectChart(imageUrl, image);
                    });
                const labelElement = $('<div>')
                    .addClass('text-center')
                    .text(image);
                const containerElement = $('<div>')
                    .addClass('chart-container')
                    .append(imgElement)
                    .append(labelElement);
                chartsContainer.append(containerElement);
            });
        });
    }

    function selectChart(imageUrl, imageName) {
        $('#selected-chart').attr('src', imageUrl);
        $('#selected-chart-label').text(imageName);
        $('#selected-chart-container').show();
        $('.chart-thumbnail').removeClass('selected');
        $('.chart-thumbnail[src="' + imageUrl + '"]').addClass('selected');
    }
});
