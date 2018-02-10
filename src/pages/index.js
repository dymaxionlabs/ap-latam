import React from 'react'
import Link from 'gatsby-link'

const IndexPage = () => (
  <div className="container">
    <section className="hero is-medium is-primary is-bold">
      <div className="hero-body">
        <div className="container">
          <h1 className="title">
            VyA Latam
          </h1>
          <h2 className="subtitle">
            Mapa de potenciales asentamientos informales y barrios precarios
          </h2>
          <p>
            El mapa está elaborado a partir de la aplicación de técnicas de&nbsp;
            <em>machine learning</em> en imágenes satelitales y otros datos
            georreferenciados.
          </p>
        </div>
      </div>
    </section>
    <section className="section">
      <div className="container">
        <h1 className="title">Explorar</h1>
        <h2 className="subtitle">Haz clic sobre el nombre de una ciudad para explorar el mapa.</h2>
        <em>[Acá va la lista de ciudades y un link para buscar]</em>
      </div>
    </section>
    <section className="section">
      <h2>Accede a los datos</h2>
      <p>
        Aquí podrás acceder a los datos presentados en el mapa, tanto la capa
        vectorial de las áreas precarias detectadas, como así también otros datos
        analíticos generados, agrupados por ciudad y fecha de actualización.
      </p>
      <Link className="button" to="/datos">Ver Datos</Link>
    </section>
    <section className="section">
      <h2>Publicaciones</h2>
      <p>En esta página podrás descargar y leer publicaciones sobre la
        metodología de detección.</p>
      <Link className="button" to="/publicaciones">Ver Publicaciones</Link>
    </section>
    <section className="section">
      <h2>Prensa</h2>
      <em>[Acá van las notas publicadas del proyecto]</em>
    </section>
    <section className="section">
      <h2>Sponsors</h2>
      <em>[Acá van los logos de los sponsors]</em>
    </section>
    <section className="section">
      <h2>Licencia</h2>
      <em>[Texto sobre licencia de la página, el uso de los datos, y las publicaciones]</em>
    </section>
    <section className="section">
      <h2>Contacto</h2>
      <em>[Acá va la sección de contacto]</em>
    </section>
  </div>
)

export default IndexPage
