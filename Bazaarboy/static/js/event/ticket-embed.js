(function() {
  Bazaarboy.event.ticket_embed = {
    requiresAddress: false,
    currentCheckout: 'HI',
    updateSubtotal: function() {
      var quantity, ticket, tickets, totalPrice, totalQuantity, _i, _len;
      tickets = $('div#tickets-canvas div.ticket.active');
      totalPrice = 0;
      totalQuantity = 0;
      for (_i = 0, _len = tickets.length; _i < _len; _i++) {
        ticket = tickets[_i];
        quantity = parseInt($(ticket).find('input.ticket-quantity').val());
        totalQuantity += quantity;
        totalPrice += quantity * parseFloat($(ticket).attr('data-price'));
      }
      $('div#tickets-subtotal span.total').html(totalPrice.toFixed(2));
      if (totalPrice !== 0) {
        $('div#tickets-subtotal span.fee').removeClass('hide');
      } else {
        $('div#tickets-subtotal span.fee').addClass('hide');
      }
      $('div#tickets-subtotal span.count').html(totalQuantity);
      if (totalQuantity === 1) {
        $('div#tickets-subtotal span.plural').addClass('hide');
      } else {
        $('div#tickets-subtotal span.plural').removeClass('hide');
      }
    },
    stripeResponseHandler: function(status, response) {
      var _this = this;
      if (status === 200) {
        Bazaarboy.post('payment/charge/', {
          checkout: this.currentCheckout,
          stripe_token: response.id
        }, function(response) {
          if (response.status === 'OK') {
            _this.completePurchase(response.tickets);
          } else {
            alert(response.message);
            $('a#tickets-confirm').html('Confirm RSVP');
          }
        });
      } else {
        console.log(response);
      }
    },
    purchase: function() {
      var address, fields, options, params, quantity, ticket, ticketSelected, tickets, _i, _len,
        _this = this;
      $('a#tickets-confirm').html('Processing...');
      params = {
        event: eventId,
        first_name: $('input[name=first_name]').val().trim(),
        last_name: $('input[name=last_name]').val().trim(),
        email: $('input[name=email]').val().trim(),
        phone: $('input[name=phone]').val().trim(),
        details: {}
      };
      if (this.requiresAddress) {
        if ($('input[name=address]').val().trim() === '' || $('input[name=state]').val().trim() === '' || $('input[name=city]').val().trim() === '' || $('input[name=zip]').val().trim() === '') {
          alert('All Address Fields Are Required');
          $('a#tickets-confirm').html('Confirm RSVP');
          return;
        }
      }
      address = $('input[name=address]').val().trim();
      if ($('input[name=city]').val().trim() !== '') {
        address += ', ' + $('input[name=city]').val().trim();
      }
      if ($('input[name=state]').val().trim() !== '') {
        address += ', ' + $('input[name=state]').val().trim();
      }
      if ($('input[name=zip]').val().trim() !== '') {
        address += ' ' + $('input[name=zip]').val().trim();
      }
      params.address = address;
      if ($('input[name=promos]').length > 0) {
        if ($('input[name=promos]').val().trim() !== '') {
          params['promos'] = $('input[name=promos]').val().trim();
        }
      }
      tickets = $('div#tickets-canvas div.ticket');
      ticketSelected = false;
      for (_i = 0, _len = tickets.length; _i < _len; _i++) {
        ticket = tickets[_i];
        if ($(ticket).hasClass('active')) {
          ticketSelected = true;
          quantity = parseInt($(ticket).find('input.ticket-quantity').val());
          params.details[$(ticket).attr('data-id')] = {
            'quantity': quantity,
            'extra_fields': {}
          };
          if ($(ticket).find('div.custom-option-group').length > 0) {
            options = $(ticket).find('div.custom-option-group');
            $.each(options, function(target) {
              if ($(this).find('div.custom-option.active').length > 0) {
                params.details[$(ticket).attr('data-id')]['extra_fields'][$(this).data('field')] = $(this).find('div.custom-option.active').data('option');
              }
            });
          }
          if ($(ticket).find('div.custom-field-group').length > 0) {
            fields = $(ticket).find('div.custom-field-group');
            $.each(fields, function(target) {
              var fieldValue;
              fieldValue = $(this).find('input.custom-field-input').val();
              if (String(fieldValue).trim() !== '') {
                return params.details[$(ticket).attr('data-id')]['extra_fields'][$(this).data('field')] = String(fieldValue).trim();
              } else {
                return params.details[$(ticket).attr('data-id')]['extra_fields'][$(this).data('field')] = ' ';
              }
            });
          }
        }
      }
      params.details = JSON.stringify(params.details);
      if (params.phone.length === 0) {
        delete params.phone;
      }
      if (!ticketSelected) {
        alert('You Must Select A Ticket');
        $('a#tickets-confirm').html('Confirm RSVP');
      } else if (params.first_name === '') {
        alert('Please Add a First Name');
        $('a#tickets-confirm').html('Confirm RSVP');
        return;
      } else if (params.last_name === '') {
        alert('Please Add a Last Name');
        $('a#tickets-confirm').html('Confirm RSVP');
        return;
      } else if (params.email === '') {
        alert('Please Add an Email');
        $('a#tickets-confirm').html('Confirm RSVP');
        return;
      } else {
        Bazaarboy.post('event/purchase/', params, function(response) {
          var a, b, total;
          if (response.status !== 'OK') {
            alert(response.message);
            return $('a#tickets-confirm').html('Confirm RSVP');
          } else {
            if (response.publishable_key == null) {
              return _this.completePurchase(response.tickets);
            } else {
              total = response.purchase.amount * 100;
              a = (1 + 0.05) * total + 50;
              b = (1 + 0.029) * total + 30 + 1000;
              total = Math.round(Math.min(a, b));
              return StripeCheckout.open({
                key: response.publishable_key,
                address: false,
                amount: total,
                currency: 'usd',
                name: response.purchase.event.name,
                description: 'Tickets for ' + response.purchase.event.name,
                panelLabel: 'Checkout',
                email: params.email,
                image: response.logo,
                closed: function() {
                  $('a#tickets-confirm').html('Confirm RSVP');
                },
                token: function(token) {
                  Bazaarboy.post('payment/charge/', {
                    checkout: response.purchase.checkout,
                    stripe_token: token.id
                  }, function(response) {
                    if (response.status === 'OK') {
                      _this.completePurchase(response.tickets);
                    } else {
                      alert(response.message);
                    }
                  });
                }
              });
              /*
              @currentCheckout = response.purchase.checkout
              Stripe.setPublishableKey response.publishable_key
              Stripe.card.createToken $("form#payment-form"), (status, response) =>
                  @stripeResponseHandler status, response
                  return
              */

            }
          }
        });
        return;
      }
    },
    completePurchase: function(tickets) {
      var k, newTicket, scope, ticket, ticketHTML;
      scope = this;
      if (!this.overlayAnimationInProgress) {
        this.overlayAnimationInProgress = true;
        $('div#confirmation-modal div.ticket').hide();
        ticketHTML = $('div#confirmation-modal div.ticket-model').html();
        for (k in tickets) {
          ticket = tickets[k];
          newTicket = $(ticketHTML);
          newTicket.find('div.quantity').html('x' + ticket['quantity']);
          newTicket.find('div.name').html(ticket['name']);
          $('div#confirmation-modal').find('div.tickets').append(newTicket);
          newTicket.show();
        }
        $('div#wrapper-overlay').animate({
          opacity: 0
        }, 300, function() {
          $(this).addClass('hide');
        });
        $('div#tickets').animate({
          opacity: 0
        }, 300, function() {
          $(this).addClass('hide');
          scope.overlayAnimationInProgress = false;
        });
        $('.ticket').find('div.ticket-middle').slideUp(100);
        $('.ticket.active').removeClass('active');
        $('a#tickets-confirm').html('Confirm RSVP');
        $('input[name=quantity]').val(0);
        $('input[name=first_name]').val('');
        $('input[name=last_name]').val('');
        $('input[name=email]').val('');
        $('input[name=phone]').val('');
        $('input[name=address]').val('');
        $('input[name=state]').val('');
        $('input[name=city]').val('');
        $('input[name=zip]').val('');
        $('input.ticket-selected').prop('checked', false);
        $('div#confirmation-modal').foundation('reveal', 'open');
      }
    },
    init: function() {
      var scope,
        _this = this;
      scope = this;
      if ($('.tix-type').length === 1) {
        scope.ticketId = $('.tix-type').data('id');
      }
      $('div.custom-option-group div.custom-option').click(function() {
        $(this).parents('div.custom-option-group').find('div.custom-option').removeClass('active');
        $(this).addClass('active');
      });
      $('div#tickets-details a.start-promo-btn').click(function() {
        return $('div.start-promo').fadeOut(300, function() {
          $('div.enter-promo').fadeIn(300);
        });
      });
      $('div#tickets-canvas div.ticket.invalid div.ticket-top').hover(function() {
        if (!$(this).parents('div.ticket').hasClass('soldout')) {
          $(this).parents('div.ticket').find('.timing-container').addClass('underline');
        }
      }, function() {
        if (!$(this).parents('div.ticket').hasClass('soldout')) {
          $(this).parents('div.ticket').find('.timing-container').removeClass('underline');
        }
      });
      $('div#tickets-canvas div.ticket.valid div.ticket-top').hover(function() {
        if (!$(this).parents('div.ticket').hasClass('soldout')) {
          $(this).parents('div.ticket').addClass('hover');
        }
      }, function() {
        if (!$(this).parents('div.ticket').hasClass('soldout')) {
          $(this).parents('div.ticket').removeClass('hover');
        }
      });
      $('div#tickets-canvas div.ticket.valid div.ticket-top').click(function() {
        var quant;
        if (!$(this).parents('div.ticket').hasClass('soldout')) {
          $(this).parents('.ticket').toggleClass('active');
          if ($(this).parents('.ticket').hasClass('active')) {
            $(this).parents('.ticket').find('div.ticket-middle').slideDown(100);
            quant = $(this).parents('.ticket').find('input.ticket-quantity');
            if (quant.val().trim() === '' || parseInt(quant.val()) === 0) {
              quant.val(1);
            }
          } else {
            $(this).parents('.ticket').find('div.ticket-middle').slideUp(100);
          }
          $('.address-container').addClass('hide');
          $('.payment-container').addClass('hide');
          scope.requiresAddress = false;
          $('div.ticket').each(function() {
            if ($(this).data('address') === 'yes' && $(this).hasClass('active')) {
              $('.address-container').removeClass('hide');
              return scope.requiresAddress = true;
            }
          });
          scope.updateSubtotal();
        }
      });
      $('input.ticket-quantity').keyup(function() {
        var wrapper;
        wrapper = $(this).closest('div.wrapper');
        if ($(this).val().trim() === '' || parseInt($(this).val()) === 0) {
          $(wrapper).find('input.ticket-selected').prop('checked', false);
        } else {
          $(wrapper).find('input.ticket-selected').prop('checked', true);
        }
        scope.updateSubtotal();
      });
      $('input.ticket-quantity').blur(function() {
        if ($(this).val().trim() === '' || parseInt($(this).val()) === 0) {
          $(this).val(0);
          $(this).parents('.ticket').removeClass('active');
          $(this).parents('.ticket').find('div.ticket-middle').slideUp(100);
        }
        scope.updateSubtotal();
      });
      $('a#tickets-confirm').click(function() {
        _this.purchase();
      });
    }
  };

  Bazaarboy.event.ticket_embed.init();

}).call(this);
