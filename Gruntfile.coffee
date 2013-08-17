module.exports = (grunt) ->
    grunt.loadNpmTasks('grunt-contrib-coffee')
    grunt.loadNpmTasks('grunt-contrib-uglify')
    grunt.loadNpmTasks('grunt-contrib-jade')
    grunt.loadNpmTasks('grunt-contrib-less')
    grunt.loadNpmTasks('grunt-contrib-concat')
    grunt.loadNpmTasks('grunt-contrib-watch')
    grunt.initConfig
        concat:
            css:
                src: [
                    'Bazaarboy/static/css/normalize.css'
                    'Bazaarboy/static/css/layout.css'
                ]
                dest: 'Bazaarboy/static/css/layout.css'
            css_admin:
                src: [
                    'Bazaarboy/static/css/normalize.css'
                    'Bazaarboy/static/admin/css/layout.css'
                ]
                dest: 'Bazaarboy/static/admin/css/layout.css'
            js:
                src: [
                    'Bazaarboy/static/js/libraries/jquery.min.js'
                    'Bazaarboy/static/js/libraries/jquery.easing.min.js'
                    'Bazaarboy/static/js/libraries/jquery.serialize-object.min.js'
                    'Bazaarboy/static/js/libraries/jquery.ui.widget.min.js'
                    'Bazaarboy/static/js/libraries/jquery.iframe-transport.min.js'
                    'Bazaarboy/static/js/libraries/jquery.fileupload.min.js'
                ]
                dest: 'Bazaarboy/static/js/libraries.js'
        jade:
            compile: 
                options:
                    data:
                        debug: false
                        pretty: true
                files: [
                    expand: true
                    cwd: 'Bazaarboy/views/templates/'
                    src: ['**/*.jade']
                    dest: 'Bazaarboy/templates/'
                    ext: '.html'
                ,
                    expand: true
                    cwd: 'Bazaarboy/views/admin/templates/'
                    src: ['**/*.jade']
                    dest: 'Bazaarboy/templates/admin/'
                    ext: '.html'
                ]
        coffee:
            compile:
                files: [
                    expand: true
                    cwd: 'Bazaarboy/views/js/'
                    src: ['**/*.coffee']
                    dest: 'Bazaarboy/static/js/'
                    ext: '.js'
                ,
                    expand: true
                    cwd: 'Bazaarboy/views/admin/js/'
                    src: ['**/*.coffee']
                    dest: 'Bazaarboy/static/admin/js/'
                    ext: '.js'
                ]
        uglify:
            compile:
                files: [
                    expand: true
                    cwd: 'Bazaarboy/static/js/'
                    src: ['**/*.js', '!libraries/**/*.js', '!libraries.js']
                    dest: 'Bazaarboy/static/js/'
                    ext: '.js'
                ,
                    expand: true
                    cwd: 'Bazaarboy/static/admin/js/'
                    src: ['**/*.js']
                    dest: 'Bazaarboy/static/admin/js/'
                    ext: '.js'
                ]
        less:
            compile:
                files: [
                    expand: true
                    cwd: 'Bazaarboy/views/css/'
                    src: ['**/*.less']
                    dest: 'Bazaarboy/static/css/'
                    ext: '.css'
                ,
                    expand: true
                    cwd: 'Bazaarboy/views/admin/css/'
                    src: ['**/*.less']
                    dest: 'Bazaarboy/static/admin/css/'
                    ext: '.css'
                ]
        watch:
            jade:
                options:
                    nospawn: true
                files: [
                    'Bazaarboy/views/templates/**/*.jade',
                    'Bazaarboy/views/admin/templates/**/*.jade'
                ]
                tasks: ['jade']
            coffee:
                options:
                    nospawn: true
                files: [
                    'Bazaarboy/views/js/**/*.coffee',
                    'Bazaarboy/views/admin/js/**/*.coffee'
                ]
                tasks: ['coffee', 'uglify']
            less:
                options:
                    nospawn: true
                files: [
                    'Bazaarboy/views/css/**/*.less'
                ]
                tasks: ['less', 'concat:css']
            less_admin:
                options:
                    nospawn: true
                files: [
                    'Bazaarboy/views/admin/css/**/*.less'
                ]
                tasks: ['less', 'concat:css_admin']
            libraries:
                options:
                    nospawn: true
                files: [
                    'Bazaarboy/static/js/libraries/**/*.js'
                ]
                tasks: ['concat:js']
    grunt.event.on 'watch', (action, filepath) ->
        parts = filepath.split('.')
        ext = parts[parts.length - 1]
        if ext is 'jade'
            output = filepath.replace(/Bazaarboy\/views/, 'Bazaarboy')
                             .replace(/\.jade/, '.html')
            if filepath.indexOf('Bazaarboy/views/admin/templates') isnt -1
                output = filepath.replace(/Bazaarboy\/views\/admin\/templates/, 
                                          'Bazaarboy/templates/admin')
                                 .replace(/\.jade/, '.html')
            opts = {}
            opts[output] = filepath
            grunt.config(['jade', 'compile', 'files'], opts)
        else if ext is 'coffee'
            output = filepath.replace(/Bazaarboy\/views/, 'Bazaarboy/static')
                             .replace(/\.coffee/, '.js')
            opts = {}
            opts[output] = filepath
            uglifyOpts = {}
            uglifyOpts[output] = output
            grunt.config(['coffee', 'compile', 'files'], opts)
            grunt.config(['uglify', 'compile', 'files'], uglifyOpts)
        else if ext is 'less'
            output = filepath.replace(/Bazaarboy\/views/, 'Bazaarboy/static')
                             .replace(/\.less/, '.css')
            opts = {}
            opts[output] = filepath
            grunt.config(['less', 'compile', 'files'], opts)
    grunt.registerTask('dev', ['jade', 'coffee', 'uglify', 'less', 'concat', 'watch'])
    return