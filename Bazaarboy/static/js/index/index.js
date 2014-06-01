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
        var sale, _i, _len;
        if (Object.keys(response.purchases).length === 0) {
          rsvps.push([launchedTime.unix() * 1000, 0]);
          sales.push([launchedTime.unix() * 1000, 0]);
        }
        $.each(response.purchases, function(index, purchase) {
          var date;
          date = moment(purchase.date, 'YYYY-MM-DD HH:mm:ss');
          rsvps.push([date.unix() * 1000, purchase.rsvps]);
          sales.push([date.unix() * 1000, purchase.amount]);
        });
        rsvps = rsvps.sort();
        sales = sales.sort();
        for (_i = 0, _len = sales.length; _i < _len; _i++) {
          sale = sales[_i];
          total_sales += sale[1];
          sale[1] = total_sales;
        }
        $(canvas).highcharts({
          chart: {
            type: 'area',
            marginTop: 20,
            style: {
              fontFamily: '"Gotham SSm A", "Gotham SSm B", sans-serif'
            }
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
            allowDecimals: false,
            lineColor: '#D6D6D6',
            gridLineColor: '#F6F6F6',
            gridLineWidth: 1,
            type: 'datetime',
            dateTimeLabelFormats: {
              millisecond: '%b %e',
              second: '%b %e',
              minute: '%b %e',
              hour: '%b %e',
              day: '%b %e'
            },
            labels: {
              style: {
                color: '#D6D6D6',
                fontWeight: 'bold'
              }
            }
          },
          yAxis: {
            lineWidth: 1,
            lineColor: '#D6D6D6',
            offset: -3,
            gridLineWidth: 0,
            labels: {
              format: '{value}'
            },
            title: {
              text: '',
              style: {
                color: '#4963E4'
              }
            },
            min: 0,
            labels: {
              style: {
                color: '#D6D6D6',
                fontWeight: 'bold'
              }
            }
          },
          plotOptions: {
            area: {
              fillOpacity: .25,
              pointStart: 0,
              marker: {
                enabled: false,
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
            }
          ]
        });
      });
    },
    loadGraph: function(eventFrame) {},
    deleteEvent: function(eventId) {
      var _this = this;
      Bazaarboy.post('event/delete/', {
        id: eventId
      }, function(response) {
        if (response.status === 'OK') {
          return 'OK';
        } else {
          alert(response.message);
        }
      });
    },
    launchEvent: function(eventId) {
      var _this = this;
      return Bazaarboy.post('event/launch/', {
        id: eventId
      }, function(response) {
        if (response.status === 'OK') {
          window.location = '/event/' + eventId + '#launch';
        } else {
          alert(response.message);
        }
      });
    },
    init: function() {
      var scope;
      scope = this;
      $('div.create-event').click(function() {
        var profileId;
        profileId = $(this).attr('data-profile-id');
        scope.createEvent(profileId);
      });
      $('a.events-filter').click(function() {
        var filter;
        $('div#wrapper-sidebar a.sidebar-item.events-filter').removeClass('selected');
        filter = $(this);
        $('#wrapper-dashboard div.event-tiles-container.active').fadeOut(300, function() {
          $('#wrapper-dashboard div.graph-canvas').empty();
          $('#wrapper-dashboard div.event-tiles-container.active').removeClass('active');
          if (filter.hasClass('events-filter-summary')) {
            $('div#wrapper-sidebar a.sidebar-item.events-filter-summary').addClass('selected');
            $('div.header-title div.text span.sub').text('Events Overview');
            $('#wrapper-dashboard div.summary-events').addClass('active');
            $('#wrapper-dashboard div.summary-events').fadeIn(300, function() {
              $('div.current-event, div.past-event').each(function() {
                scope.initGraph(this);
              });
            });
          }
          if (filter.hasClass('events-filter-current')) {
            $('div#wrapper-sidebar a.sidebar-item.events-filter-current').addClass('selected');
            $('div.header-title div.text span.sub').text('Current Events');
            $('#wrapper-dashboard div.current-events').addClass('active');
            $('#wrapper-dashboard div.current-events').fadeIn(300, function() {
              $('div.current-event').each(function() {
                scope.initGraph(this);
              });
            });
          }
          if (filter.hasClass('events-filter-draft')) {
            $('div#wrapper-sidebar a.sidebar-item.events-filter-draft').addClass('selected');
            $('div.header-title div.text span.sub').text('Draft Events');
            $('#wrapper-dashboard div.draft-events').addClass('active');
            $('#wrapper-dashboard div.draft-events').fadeIn(300);
          }
          if (filter.hasClass('events-filter-past')) {
            $('div#wrapper-sidebar a.sidebar-item.events-filter-past').addClass('selected');
            $('div.header-title div.text span.sub').text('Past Events');
            $('#wrapper-dashboard div.past-events').addClass('active');
            $('#wrapper-dashboard div.past-events').fadeIn(300, function() {
              $('div.past-event').each(function() {
                scope.initGraph(this);
              });
            });
          }
        });
      });
      $('div.draft-event a.delete-draft').click(function(e) {
        var deleteConfirm, eventId;
        e.preventDefault();
        deleteConfirm = confirm("All information (including RSVPs) from this event will be lost. Are you sure you want to delete?");
        eventId = $(this).data('id');
        if (deleteConfirm) {
          eventId = $(this).data('id');
          scope.deleteEvent(eventId);
          $(this).parents('div.draft-event').fadeOut();
        }
      });
      $('div.draft-event a.launch-draft').click(function(e) {
        var eventId;
        eventId = $(this).data('id');
        scope.launchEvent(eventId);
        $(this).html("Launching...");
      });
      $('div.current-event, div.past-event').each(function() {
        scope.initGraph(this);
      });
    }
  };

  Bazaarboy.index.index.init();

}).call(this);
