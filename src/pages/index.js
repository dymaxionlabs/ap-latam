import React from 'react'
import Link from 'gatsby-link'

const IndexPage = () => (
  <div>
    <h1>Mapa de potenciales villas y asentamientos</h1>
    <p>El mapa está elaborado a partir de la aplicación de técnicas de
      <em>machine learning</em> en imágenes satelitales y otros datos
      georreferenciados.</p>
    <p>
      <em>Acá va la lista de ciudades</em>
      <em>[Acá va la lista de ciudades y un link para buscar]</em>
    </p>
    <section>
      <h2>Accede a los datos</h2>
      <p>
        Aquí podrás acceder a los datos presentados en el mapa, tanto la capa
        vectorial de las áreas precarias detectadas, como así también otros datos
        analíticos generados, agrupados por ciudad y fecha de actualización.
      </p>
      <Link to="/datos">Ver Datos</Link>
    </section>
    <section>
      <h2>Publicaciones</h2>
      <p>En esta página podrás descargar y leer publicaciones sobre la
        metodología de detección.</p>
      <Link to="/publicaciones">Ver Publicaciones</Link>
    </section>
    <section>
      <h2>Prensa</h2>
      <em>[Acá van las notas publicadas del proyecto]</em>
    </section>
    <section>
      <h2>Sponsors</h2>
      <em>[Acá van los logos de los sponsors]</em>
    </section>
    <section>
      <h2>Licencia</h2>
      <em>[Texto sobre licencia de la página, el uso de los datos, y las publicaciones]</em>
    </section>
    <section>
      <h2>Contacto</h2>
      <em>[Acá va la sección de contacto]</em>
    </section>
  </div>
)

export default IndexPage
