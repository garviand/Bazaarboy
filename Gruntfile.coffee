module.exports = (grunt) ->
    grunt.loadNpmTasks('grunt-contrib-coffee')
    grunt.loadNpmTasks('grunt-contrib-jade')
    grunt.loadNpmTasks('grunt-contrib-less')
    grunt.loadNpmTasks('grunt-contrib-watch')
    grunt.initConfig
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
                ]
        coffee:
            compile:
                files: [
                    expand: true
                    cwd: 'Bazaarboy/views/js/'
                    src: ['**/*.coffee']
                    dest: 'Bazaarboy/static/js/'
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
                ]
        watch:
            jade:
                options:
                    nospawn: true
                files: 'Bazaarboy/views/templates/**/*.jade'
                tasks: ['jade']
            coffee:
                options:
                    nospawn: true
                files: 'Bazaarboy/views/js/**/*.coffee'
                tasks: ['coffee']
            less:
                options:
                    nospawn: true
                files: 'Bazaarboy/views/css/**/*.less'
                tasks: ['less']
    grunt.event.on 'watch', (action, filepath) ->
        parts = filepath.split('.')
        ext = parts[parts.length - 1]
        if ext is 'jade'
            output = filepath.replace(/Bazaarboy\/views/, 'Bazaarboy')
                             .replace(/\.jade/, '.html')
            opts = {}
            opts[output] = filepath
            grunt.config(['jade', 'compile', 'files'], opts)
        else if ext is 'coffee'
            output = filepath.replace(/Bazaarboy\/views\/js/, 'Bazaarboy/static/js')
                             .replace(/\.coffee/, '.js')
            opts = {}
            opts[output] = filepath
            grunt.config(['coffee', 'compile', 'files'], opts)
        else if ext is 'less'
            output = filepath.replace(/Bazaarboy\/views\/css/, 'Bazaarboy/static/css')
                             .replace(/\.less/, '.css')
            opts = {}
            opts[output] = filepath
            grunt.config(['less', 'compile', 'files'], opts)
    grunt.registerTask('dev', ['jade', 'coffee', 'less', 'watch'])
    return