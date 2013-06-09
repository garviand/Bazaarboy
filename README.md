# Bazaarboy

  Bazaarboy is the next generation local event solution. The platform roots in the Django framework.

  `fab compile` compiles all the sugar files (jade, less, coffeescript) into proper format.
  `fab dev` starts the development environment by compiling all necessary files and start the Django development server at port 8080 (or you can change it by `fab dev:port=DESIRED_PORT`). All changes on the model will be automatically migrated using South.