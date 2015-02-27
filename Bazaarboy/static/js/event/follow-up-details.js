(function() {
  Bazaarboy.event.follow_up_details = {
    sending: false,
    init: function() {
      var clickData, initData, openData, scope;
      scope = this;
      initData = {
        chart: {
          plotBackgroundColor: null,
          plotBorderWidth: null,
          plotShadow: false
        },
        title: {
          verticalAlign: 'middle',
          floating: true,
          style: {
            color: '#FFF',
            fontSize: '42px',
            fontWeight: '300',
            fontFamily: '\'Gotham SSm A\', \'Gotham SSm B\', sans-serif'
          }
        },
        colors: ["#F3A536", "#D4D4D4"],
        legend: {
          enabled: false
        },
        credits: {
          enabled: false
        },
        tooltip: {
          enabled: false
        },
        plotOptions: {
          pie: {
            borderWidth: 0,
            allowPointSelect: false,
            dataLabels: {
              enabled: false
            },
            marker: {
              enabled: false,
              symbol: 'circle',
              radius: 2,
              states: {
                hover: {
                  enabled: false
                }
              }
            }
          }
        }
      };
      openData = initData;
      openData.series = [
        {
          type: 'pie',
          name: 'Invite Opens',
          data: [
            {
              name: 'Opens',
              y: totalOpens
            }, ['Reciptients', recipients - totalOpens]
          ]
        }
      ];
      openData.title.text = openPercent;
      $('div.open-graph').highcharts(openData);
      clickData = initData;
      clickData.series = [
        {
          type: 'pie',
          name: 'Invite Clicks',
          data: [
            {
              name: 'Clicks',
              y: totalClicks
            }, ['Reciptients', recipients - totalClicks]
          ]
        }
      ];
      clickData.title.text = clickPercent;
      $('div.click-graph').highcharts(clickData);
    }
  };

  Bazaarboy.event.follow_up_details.init();

}).call(this);
