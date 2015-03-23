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

RedactorPlugins.video = function()
  {
  return {
    reUrlYoutube: /https?:\/\/(?:[0-9A-Z-]+\.)?(?:youtu\.be\/|youtube\.com\S*[^\w\-\s])([\w\-]{11})(?=[^\w\-]|$)(?![?=&+%\w.-]*(?:['"][^<>]*>|<\/a>))[?=&+%\w.-]*/ig,
    reUrlVimeo: /https?:\/\/(www\.)?vimeo.com\/(\d+)($|\/)/,
    getTemplate: function()
    {
      return String()
      + '<section id="redactor-modal-video-insert">'
        + '<label>' + this.lang.get('video_html_code') + '</label>'
        + '<textarea id="redactor-insert-video-area" style="height: 160px;"></textarea>'
      + '</section>';
    },
    init: function()
    {
      var button = this.button.addAfter('image', 'video', this.lang.get('video'));
      this.button.addCallback(button, this.video.show);
    },
    show: function()
    {
      this.modal.addTemplate('video', this.video.getTemplate());

      this.modal.load('video', this.lang.get('video'), 700);
      this.modal.createCancelButton();

      var button = this.modal.createActionButton(this.lang.get('insert'));
      button.on('click', this.video.insert);

      this.selection.save();
      this.modal.show();

      $('#redactor-insert-video-area').focus();

    },
    insert: function()
    {
      var data = $('#redactor-insert-video-area').val();

      if (!data.match(/<iframe|<video/gi))
      {
        data = this.clean.stripTags(data);

        // parse if it is link on youtube & vimeo
        var iframeStart = '<iframe style="width: 100%; height: 350px;" src="',
          iframeEnd = '" frameborder="0" allowfullscreen></iframe>';

        if (data.match(this.video.reUrlYoutube))
        {
          data = data.replace(this.video.reUrlYoutube, iframeStart + '//www.youtube.com/embed/$1' + iframeEnd);
        }
        else if (data.match(this.video.reUrlVimeo))
        {
          data = data.replace(this.video.reUrlVimeo, iframeStart + '//player.vimeo.com/video/$2' + iframeEnd);
        }
      }

      this.selection.restore();
      this.modal.close();

      var current = this.selection.getBlock() || this.selection.getCurrent();

      if (current) $(current).after(data);
      else
      {
        this.insert.html(data);
      }

      this.code.sync();
    }

  };
};