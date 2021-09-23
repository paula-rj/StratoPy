# maquina virtual python
crear maquina virtual 
> python -m venv /path/de/mi/maquina/<nombre de mi maquina nueva>

activar
> source <nombre de mi maquina nueva>/bin/activate

desactivar
> deactivate

listar paquetes
> pip list

verificar lista de ambientes
> lsvirtualenv

# maquina virtual anaconda
crear maquina virtual
> conda create --name <nombre de mi maquina nueva>

activar
> conda activate <nombre de mi maquina nueva>

desactivar (cuando hayas terminados las tareas)
> conda deactivate

listar paquetes
> conda list

instalar yml
> conda env create -f puppies.yml

---

configurar el virtualenvwrap
sigue el paso a paso del manual