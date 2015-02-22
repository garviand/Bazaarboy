if (!RedactorPlugins) var RedactorPlugins = {};

RedactorPlugins.instagram = function(){
  return{
    getTemplate: function(){
      return String()
      + '<section id="redactor-modal-advanced">'
      + '<label>Insert Instagram Slideshow</label>'
      + '<input style="display:block; margin-top:20px;" type="text" id="mymodal-textarea", placeholder="Enter Hashtag" />'
      + '</section>';
    },
    init: function(){
      var button = this.button.add('instagram', 'Instagram');
      this.button.setAwesome('instagram', 'fa-instagram');
      this.button.addCallback(button, this.instagram.show);
    },
    show: function(){
      this.modal.addTemplate('instagram', this.instagram.getTemplate());
      this.modal.load('instagram', 'Enter Hashtag', 400);
      this.modal.createCancelButton();
      var button = this.modal.createActionButton('Insert Slideshow');
      button.on('click', this.instagram.insert);
      this.selection.save();
      this.modal.show();
      $('#mymodal-textarea').focus();
    },
    insert: function(){
      hashtag = $('#mymodal-textarea').val();
      this.modal.close();
      this.selection.restore();
      scope = this
      scope.insert.html('<iframe frameborder="0" width="100%" height="220" scrolling="no" src="/event/instagram/?hashtag=' + hashtag + '&event_id=' + eventId + '">', false);
      scope.code.sync();
    }
  };
};