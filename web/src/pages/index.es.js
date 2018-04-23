import React from 'react'
import Link from 'gatsby-link'
import Footer from './_footer.es'
import { CityList, CityListItem } from '../components/city_list'
import { NewsList, NewsListItem } from '../components/news_list'

import mapboxLogo from '../assets/mapbox-logo-color.png'
import techoLogo from '../assets/techo-logo.png'

const IndexPage = ({ data }) => {
  const cities = data.allCitiesJson.edges.map(v => v.node)

  return (
    <div>
      <section className="hero is-medium is-primary is-bold">
        <div className="logo hero-body">
          <div className="container">
            <h1 className="title is-1">{data.site.siteMetadata.name}</h1>
            <h2 className="subtitle is-4">
              Monitor de potenciales asentamientos informales y barrios
              precarios
            </h2>
            <div className="content">
              <p>
                El mapa está elaborado a partir de la aplicación de técnicas
                de&nbsp;
                <em>machine learning</em> en imágenes satelitales y otros datos
                georreferenciados.
              </p>
            </div>
          </div>
        </div>
      </section>
      <section className="section">
        <div className="container">
          <h1 className="title">Explorar</h1>
          <h2 className="subtitle">
            Haz clic sobre el nombre de una ciudad para explorar el mapa.
          </h2>
          <CityList prefix="/es" items={cities} />
        </div>
      </section>
      <section className="section">
        <div className="container">
          <h1 className="title">Accede a los datos</h1>
          <div className="content">
            <p>
              Aquí podrás acceder a los datos presentados en el mapa, tanto la
              capa vectorial de las áreas precarias detectadas, como así también
              otros datos analíticos generados, agrupados por ciudad y fecha de
              actualización.
            </p>
            <Link className="button is-primary" to="/es/data">
              Ver Datos
            </Link>
          </div>
        </div>
      </section>
      <section className="section">
        <div className="container">
          <h1 className="title">Publicaciones</h1>
          <div className="content">
            <p>
              En esta página podrás descargar y leer publicaciones sobre la
              metodología de detección.
            </p>
            <Link className="button is-primary" to="/es/publications">
              Ver Publicaciones
            </Link>
          </div>
        </div>
      </section>
      <section className="section">
        <div className="container">
          <h1 className="title">Prensa</h1>
          <div className="content">
            <NewsList items={data.site.siteMetadata.press} />
          </div>
        </div>
      </section>
      <section className="section">
        <div className="container">
          <h1 className="title">Con el apoyo de</h1>
          <div className="has-text-centered">
            <ul className="sponsors">
              <li>
                <a href="https://www.mapbox.com">
                  <img src={mapboxLogo} alt="Mapbox" />
                </a>
              </li>
              <li>
                <a href="https://www.techo.org/">
                  <img src={techoLogo} alt="TECHO" />
                </a>
              </li>
            </ul>
          </div>
        </div>
      </section>
      <section className="section">
        <div className="container">
          <h1 className="title">Licencia</h1>
          <div className="content">
            <p>
              Los datos disponibles para descargar fueron publicados bajo la{' '}
              <strong>
                Licencia de Dominio Público de Open Data Commons 1.0
              </strong>, de Open Data Commons.<br />
              Es libre de copiar, distribuir y dar uso de los datos, producir
              nuevos trabajos en base a éstos, y de modificar y transformarlos.
            </p>
            <a
              className="button is-primary"
              href="https://opendatacommons.org/licenses/pddl/"
              target="_blank"
            >
              Ver Licencia
            </a>
          </div>
        </div>
      </section>
      <section className="section">
        <div className="container">
          <h1 className="title">Contacto</h1>
          <div className="content">
            <p>
              Si tiene alguna duda sobre la metodología o los datos ofrecidos,
              no dude en contactarnos por{' '}
              <a href="mailto:contacto@dymaxionalabs.com">e-mail</a>
            </p>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  )
}

export const query = graphql`
  query IndexEsQuery {
    ...IndexFragment
  }
`

export default IndexPage
