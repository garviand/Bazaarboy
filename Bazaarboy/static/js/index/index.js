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
      var canvas, launchedTime, now;
      launchedTime = $(eventFrame).attr('data-launched-time');
      launchedTime = moment(launchedTime, 'YYYY-MM-DD HH:mm:ss');
      now = moment();
      canvas = $(eventFrame).find('div.graph-canvas');
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
            data: [[launchedTime.unix() * 1000, 0], [now.unix() * 1000, 0]]
          }, {
            name: 'Total Sale',
            type: 'spline',
            yAxis: 1,
            data: [[launchedTime.unix() * 1000, 0], [now.unix() * 1000, 0]]
          }
        ]
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
