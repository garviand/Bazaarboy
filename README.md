# Bazaarboy

  Bazaarboy is the next generation local event solution. The platform roots in the Django framework.

  To install, first make sure you have the LAMP stack in your machine, then make sure you create an empty database in mysql called `bazaarboy`. You will also need the Node.js environment, the preferred version here is 0.10.10, but others can pass for now. For Mac, you can simply download the installer; for Linux, you need to download the source code (not the binary) and compile (do: `./configure`, `make`, `make install`).

  `fab compile` compiles all the sugar files (jade, less, coffeescript) into proper format.
  
  `fab dev` starts the development environment by compiling all necessary files and start the Django development server at port 8080 (or you can change it by `fab dev:port=DESIRED_PORT`). All changes on the model will be automatically migrated using South.