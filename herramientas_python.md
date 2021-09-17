# Ambientes virtuales
> virtualenv (la mas comun y la que vamos a usar)
> python env (viene con python) <- esta crea el ambiente con la version de python de tu maquina
> conda <- no es buena para desarrollo de software
> pyenv (es la mas moderna) <- esta con la ultima actualizacion

## Virtualenv
Instalacion en debian o ubuntu
> sudo apt-get install python-virtualenv

Creando entorno virtual
- virtualenv envname
Creando entorno virtual con version de python específica
- virtualenv -p /usr/bin/python3.9 envname
- virtualenv -p $(which python3.9) envname

Activando entorno virtual
- source bin/activate

Salir del entorno virtual
- deactivate

Para administrar mejor los proyectos
- virtualenvwrapper

Para verificar el arbol de dependencias
- pip install pipdeptree

Para mostrar las dependencias que instalo el usuario
- pipdeptree | grep -P '^\w+' 