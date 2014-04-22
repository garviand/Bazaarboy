(function() {
  Bazaarboy.index.index = {
    createEvent: function(profileId) {
      var _this = this;
      Bazaarboy.post('event/create/', {
        profile: profileId
      }, function(response) {
        if (response.status === 'OK') {
          Bazaarboy.redirect('event/' + response.event.pk + '/basics/');
        } else {
          alert(response.message);
        }
      });
    },
    initGraph: function(eventFrame) {
      var canvas, eventId, launchedTime, now, rsvps, sales, total_sales,
        _this = this;
      eventId = $(eventFrame).data('id');
      launchedTime = $(eventFrame).attr('data-launched-time');
      launchedTime = moment(launchedTime, 'YYYY-MM-DD HH:mm:ss');
      now = moment();
      canvas = $(eventFrame).find('div.graph-canvas');
      rsvps = [];
      sales = [];
      total_sales = 0;
      Bazaarboy.get('event/data/', {
        id: eventId
      }, function(response) {
        if (Object.keys(response.purchases).length === 0) {
          rsvps.push([launchedTime.unix() * 1000, 0]);
          sales.push([launchedTime.unix() * 1000, 0]);
        }
        $.each(response.purchases, function(index, purchase) {
          var date;
          date = moment(purchase.date, 'YYYY-MM-DD HH:mm:ss');
          total_sales += purchase.amount;
          rsvps.push([date.unix() * 1000, purchase.rsvps]);
          sales.push([date.unix() * 1000, total_sales]);
        });
        $(canvas).highcharts({
          chart: {
            type: 'area'
          },
          credits: {
            enabled: false
          },
          colors: ["#4963E4", "#00BD84"],
          title: {
            text: ''
          },
          legend: {
            enabled: false
          },
          xAxis: {
            gridLineWidth: 0,
            type: 'datetime',
            dateTimeLabelFormats: {
              day: '%b %e'
            }
          },
          yAxis: [
            {
              labels: {
                format: '{value}'
              },
              title: {
                text: 'RSVPs',
                style: {
                  color: '#4963E4'
                }
              },
              min: 0
            }, {
              labels: {
                format: '${value}'
              },
              title: {
                text: 'Total Sales',
                style: {
                  color: '#00BD84'
                }
              },
              opposite: true,
              min: 0
            }
          ],
          plotOptions: {
            area: {
              fillOpacity: .1,
              pointStart: 0,
              marker: {
                enabled: true,
                symbol: 'circle',
                radius: 2,
                states: {
                  hover: {
                    enabled: true
                  }
                }
              }
            }
          },
          series: [
            {
              name: 'RSVPs',
              yAxis: 0,
              data: rsvps
            }, {
              name: 'Total Sales',
              yAxis: 1,
              data: sales
            }
          ]
        });
      });
    },
    loadGraph: function(eventFrame) {},
    init: function() {
      var scope;
      scope = this;
      $('div.create-event').click(function() {
        var profileId;
        profileId = $(this).attr('data-profile-id');
        scope.createEvent(profileId);
      });
      $('div.current-event').each(function() {
        scope.initGraph(this);
      });
    }
  };

  Bazaarboy.index.index.init();

}).call(this);
