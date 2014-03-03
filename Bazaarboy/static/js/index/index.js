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
      rsvps = [[launchedTime.unix() * 1000, 0]];
      sales = [[launchedTime.unix() * 1000, 0]];
      total_sales = 0;
      Bazaarboy.get('event/data/', {
        id: eventId
      }, function(response) {
        var date, purchase, _i, _len, _ref;
        _ref = response.purchases;
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          purchase = _ref[_i];
          date = moment(purchase.date, 'YYYY-MM-DD HH:mm:ss');
          total_sales += purchase.amount;
          rsvps.push([date.unix() * 1000, purchase.rsvps]);
          sales.push([date.unix() * 1000, total_sales]);
        }
        $(canvas).highcharts({
          title: {
            text: null
          },
          credits: {
            enabled: false
          },
          xAxis: {
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
                text: 'RSVPs'
              },
              min: 0
            }, {
              labels: {
                format: '${value}'
              },
              title: {
                text: 'Total Sale'
              },
              opposite: true,
              min: 0
            }
          ],
          series: [
            {
              name: 'RSVPs',
              type: 'spline',
              yAxis: 0,
              data: rsvps
            }, {
              name: 'Total Sale',
              type: 'spline',
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
