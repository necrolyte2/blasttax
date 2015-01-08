.. blasttax documentation master file, created by
   sphinx-quickstart on Thu Jan  8 16:35:32 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

========
blasttax
========

blasttax is meant to ease the viewing of the phylogony for any given taxid from
a blast report.

You just need to ensure you have the taxonomy dmp files downloaded which is pretty
simple:

.. code-block:: bash

    wget http://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump.tar.gz -O- | tar xzf -

Then you can just run blasttax on the resulting names, nodes and divisions file as
follows:

.. code-block:: bash

    $> blasttax names.dmp nodes.dmp division.dmp 7165
    African malaria mosquito(species) -> gambiae species complex(no rank) -> 
    Pyretophorus(no rank) -> Cellia(subgenus) -> Anopheles(genus) -> 
    Anophelinae(subfamily) -> Culicidae(family) -> Culicoidea(superfamily) -> 
    Culicimorpha(infraorder) -> Nematocera(suborder) -> Diptera(order) -> 
    Endopterygota(infraclass) -> Neoptera(subclass) -> Pterygota(no rank) -> 
    Dicondylia(no rank) -> Insecta(class) -> Atelocerata(superclass) -> 
    Pancrustacea(no rank) -> Mandibulata(no rank) -> Arthropoda(phylum) -> 
    Panarthropoda(no rank) -> Ecdysozoa(no rank) -> Protostomia(no rank) -> 
    Bilateria(no rank) -> Eumetazoa(no rank) -> Animalia(kingdom) -> 
    Fungi/Metazoa group(no rank) -> Eucarya(superkingdom) -> biota(no rank)

Table of Contents
-----------------

.. toctree::
    :maxdepth: 2

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
