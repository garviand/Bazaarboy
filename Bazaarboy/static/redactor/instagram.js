if (!RedactorPlugins) var RedactorPlugins = {};

RedactorPlugins.instagram = function(){
  return{
    init: function(){
      var button = this.button.add('instagram', 'Instagram');
      this.button.setAwesome('instagram', 'fa-instagram');
      this.button.addCallback(button, this.instagram.show);
    },
    show: function(){
      console.log('show');
    }
  };
};