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
            marginTop: 30,
            marginRight: 20,
            style: {
              fontFamily: 'helvetica'
            }
          },
          credits: {
            enabled: false
          },
          colors: ["#C57724", "#00BD84"],
          title: {
            text: ''
          },
          legend: {
            enabled: false
          },
          tooltip: {
            formatter: function() {
              return Highcharts.dateFormat('%b %e', new Date(this.x)) + '<br /><b>' + this.y + ' RSVPs</b>';
            },
            backgroundColor: '#C57724',
            borderWidth: 0,
            dateTimeLabelFormats: {
              millisecond: '%b %e',
              second: '%b %e',
              minute: '%b %e',
              hour: '%b %e',
              day: '%b %e',
              week: '%b %e'
            },
            style: {
              color: '#FFF'
            },
            shadow: false
          },
          xAxis: {
            allowDecimals: false,
            lineColor: '#D6D6D6',
            gridLineColor: '#F6F6F6',
            gridLineWidth: 1,
            tickLength: 0,
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
      $('div.active-rewards a.show-btn').click(function() {
        return $('div.active-rewards div.reward-list').slideDown(200);
      });
      $('div.request a.accept-request').click(function() {
        var requestId, thisRequest;
        requestId = $(this).data('id');
        thisRequest = $(this).closest('div.request');
        Bazaarboy.post('event/organizer/request/accept/', {
          id: requestId
        }, function(response) {
          if (response.status === 'OK') {
            thisRequest.html('<div class="small-12 text columns">Request Accepted! Refreshing...</div>');
            setTimeout(function() {
              return location.reload();
            }, 1000);
          } else {
            swal(response.message);
          }
        });
      });
      $('div.request a.reject-request').click(function() {
        var requestId, thisRequest;
        requestId = $(this).data('id');
        thisRequest = $(this).closest('div.request');
        swal({
          title: "Are You Sure?",
          text: "Are you sure you want to reject this collaboration request?",
          type: "warning",
          showCancelButton: true,
          confirmButtonText: "Yes",
          closeOnConfirm: true
        }, function() {
          return Bazaarboy.post('event/organizer/request/reject/', {
            id: requestId
          }, function(response) {
            if (response.status === 'OK') {
              thisRequest.html('<div class="small-12 text columns">Request Rejected...</div>');
            } else {
              swal(response.message);
            }
          });
        });
      });
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
              $('div.current-event, div.past-event, div.past-event-attention').each(function() {
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
      $('a.add-to-list-btn').click(function(e) {
        $('div#add-list-modal span.event-name').html($(this).data('name'));
        $('div#add-list-modal span.attendee-count').html($(this).data('count'));
        $('div#add-list-modal input[name=event_id]').val($(this).data('id'));
        $('div#add-list-modal').foundation('reveal', 'open');
      });
      $(document).on('close.fndtn.reveal', 'div#add-list-modal', function() {
        $('div#add-list-modal input[name=event_id]').val('');
        $('div#add-list-modal div.list').removeClass('active');
      });
      $('div#add-list-modal a.add-cancel-btn').click(function(e) {
        $('div#add-list-modal').foundation('reveal', 'close');
      });
      $('body').on('click', 'div#add-list-modal div.list', function(e) {
        $(this).toggleClass('active');
      });
      $('div#add-list-modal a.create-list').click(function() {
        var eventId, list_name, profileId;
        $('div#add-list-modal div.status').html('Creating...');
        $('div#add-list-modal div.submit-actions a').css('display', 'none');
        profileId = $('div#add-list-modal input[name=profile_id]').val();
        eventId = $('div#add-list-modal input[name=event_id]').val();
        list_name = $('div#add-list-modal input[name=list_name]').val();
        if (list_name.trim() !== '') {
          Bazaarboy.post('lists/create/', {
            profile: profileId,
            name: list_name,
            is_hidden: 1
          }, function(response) {
            var listId;
            if (response.status === 'OK') {
              listId = response.list.pk;
              $('div#add-list-modal div.status').html('Successfully Created List! Adding Members...');
              Bazaarboy.post('lists/add/event/', {
                id: listId,
                event: eventId
              }, function(response) {
                var newList;
                if (response.status === 'OK') {
                  newList = $('div.list-template').clone();
                  newList.attr('data-id', response.list.pk);
                  newList.find('div.list-name').html(response.list.name);
                  newList.find('div.list-action').html(response.added + ' Members');
                  newList.removeClass('hide');
                  $('div#add-list-modal div.lists').prepend(newList);
                  $('div#add-list-modal div.status').html('Congrats! List was Created and ' + response.added + ' Attendees were added.');
                } else {
                  swal('List Was Created, But there was an error: ' + response.message);
                }
                $('div#add-list-modal div.submit-actions a').css('display', 'block');
              });
            } else {
              swal('Could not create list');
              $('div#add-list-modal div.submit-actions a').css('display', 'block');
            }
            $('div#add-list-modal input[name=list_name]').val('');
          });
        } else {
          swal('List name can\'t be empty');
          $('div#add-list-modal div.submit-actions a').css('display', 'block');
        }
      });
      $('div#add-list-modal a.submit-add-btn').click(function() {
        var error_lists, eventId, num_finished, num_lists, selected_lists;
        $('div#add-list-modal div.status').html('Adding Attendees to Lists...');
        $('div#add-list-modal div.submit-actions a').css('display', 'none');
        eventId = $('div#add-list-modal input[name=event_id]').val();
        selected_lists = $('div#add-list-modal div.lists div.list.active');
        num_lists = selected_lists.length;
        error_lists = 0;
        num_finished = 0;
        if (num_lists > 0) {
          $.each(selected_lists, function(list) {
            Bazaarboy.post('lists/add/event/', {
              id: $(this).data('id'),
              event: eventId
            }, function(response) {
              if (response.status === 'OK') {
                $('div#add-list-modal div.status').html(num_finished + 'Lists Complete - ' + (num_lists - num_finished) + 'Lists Remaining');
              } else {
                error_lists++;
              }
              num_finished++;
              if ((num_lists - num_finished) === 0) {
                if (error_lists > 0) {
                  swal('Lists added, but some attendees may have been left out');
                } else {
                  swal({
                    title: "Success",
                    text: "The Attendees have been Added!",
                    type: "success"
                  }, function() {
                    $('div#add-list-modal').foundation('reveal', 'close');
                  });
                }
                $('div#add-list-modal div.status').html('&nbsp;');
                $('div#add-list-modal div.submit-actions a').css('display', 'block');
              }
            });
          });
        } else {
          swal('You Must Select at least One List!');
        }
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
