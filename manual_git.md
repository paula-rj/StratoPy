Comenzar el git 
> git init

Hacer una copia del repositorio
> git clone htpps://...... <nombre_pasta>

Crear un punto de la historia 
> git add <nombre del archivo>
> git commit -m "adiciona algun texto..."

Verificar los puntos en la historia
> git log

Verificar cual es el estado de los archivos
> git status

Adicionar un archivo para el repositorio
> git add <nombre del archivo>
> git commit -m "adiciona algun texto..." 

Verificar los cambios en el proyecto
> git log

Verificar un punto en especifico
> git show "numero"

verificar el ultimo punto
> git show

Vamos a crear una ramificacion
> git branch <nombre de la ramificacion>

Para irnos a la ramificacion
> git checkout <nombre de la ramificacion>

Volver a la ramificacion principal
> git checkout master

Adicionar nuevas funcionalidades al principal
> git merge <nombre de la ramificacion>

Deletar a ramificacion de la nueva funcionalidad
> git branch -D <nombre de la ramificacion>

---
---
Colocar el proyecto en la nuve
> git remote add origin https://github.com.................

Ver los respositorios remotos
> git remote -v

Empujar el repositorio local para el repositorio online
> git push -u origin master

---
otra fijacion
Adicionar todas los archivos del archivo
> git add .
> git commit -m "mensaje"

Colocar en la nuve
> git push

Configurar credenciales (para que no te vuelva a pedir contraseña)
> git config credential.helper store

---
Trabajar con un proyecto ya iniciado y resolver problemas
> git clone <link del proyecto>

criar una nueva ramificacion e ir para ella
> git checkout -b <nombre>

Cuando haces el merge te devuelve un mensaje diciendo que hay un conflicto.
Despues de resolver el conflicto es necesario volver a adicionar, comitar y mergear


---
Antes de enviar la solucion debemos actualziar 
Descargar las alteraciones que otros realizaron en el github
> git pull

---
Volver un archivo a un deternubado momento
> git checkout  <punto de la linea de tiempo> -- <nombre del archivo>

---
Recuperar algo borrado desde la ultima edicion
> git checkout -- <nombre de archivo>

