import React from 'react'
import Link from 'gatsby-link'
import Footer from '../components/footer'

import styles from './index.sass'
import mapboxLogo from '../assets/mapbox-logo-color.png'

const CityList = props => (
  <ul>{props.items.map(item => <CityListItem key={item.internalId} item={item} />)}</ul>
)

const CityListItem = props => {
  const url = `/map?id=${props.item.internalId}`
  const name = `${props.item.name}, ${props.item.country}`
  return (
    <li>
      <Link to={url}>{name}</Link>
    </li>
  )
}

const NewsList = props => (
  <table className="table is-fullwidth">
    {props.items.map(item => <NewsListItem key={item.url} item={item} />)}
  </table>
)

const NewsListItem = props => (
  <tr>
    <th>{props.item.name}</th>
    <td><a href={props.item.url} target="_blank">{props.item.title}</a></td>
  </tr>
)

const IndexPage = ({ data }) => {
  const cities = data.allCitiesJson.edges.map(v => v.node)

  return (
    <div>
      <section className="hero is-medium is-primary is-bold">
        <div className="hero-body">
          <div className="container">
            <h1 className="title is-1">{data.site.siteMetadata.name}</h1>
            <h2 className="subtitle is-4">
              Mapa de potenciales asentamientos informales y barrios precarios
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
          <CityList items={cities} />
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
            <Link className="button is-primary" to="/data">
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
            <Link className="button is-primary" to="/publications">
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
              <li><a href="https://www.mapbox.com"><img src={mapboxLogo} alt="Mapbox" /></a></li>
            </ul>
          </div>
        </div>
      </section>
      <section className="section">
        <div className="container">
          <h1 className="title">Licencia</h1>
          <div className="content">
            <p>
              {/* Texto sobre licencia de la página, el uso de los datos, y las
                  publicaciones */}
            </p>
            <Link className="button is-primary" to="/license">
              Ver Licencia
            </Link>
          </div>
        </div>
      </section>
      <section className="section">
        <div className="container">
          <h1 className="title">Contacto</h1>
          <div className="content">
            <p>Si tiene alguna duda sobre la metodología o los datos ofrecidos, no dude en contactarnos por <a href="mailto:contacto@dymaxionalabs.com">e-mail</a></p>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  )
}

export const query = graphql`
  query IndexQuery {
    site {
      siteMetadata {
        name
        press {
          name
          title
          url
        }
      }
    }
    allCitiesJson {
      edges {
        node {
          internalId
          name
          country
          path
        }
      }
    }
  }
`

export default IndexPage
