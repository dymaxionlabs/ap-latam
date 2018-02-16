import React from 'react'
import Link from 'gatsby-link'
import Footer from './_footer.en'
import { CityList, CityListItem } from '../components/city_list'
import { NewsList, NewsListItem } from '../components/news_list'

import mapboxLogo from '../assets/mapbox-logo-color.png'

const IndexPage = ({ data }) => {
  const cities = data.allCitiesJson.edges.map(v => v.node)

  return (
    <div>
      <section className="hero is-medium is-primary is-bold">
        <div className="logo hero-body">
          <div className="container">
            <h1 className="title is-1">{data.site.siteMetadata.name}</h1>
            <h2 className="subtitle is-4">
              Monitor of potential slums and informal settlements.
            </h2>
            <div className="content">
              <p>
                This map is based on the application of{' '}
                <em>machine learning</em> techniques on satellite images and
                other georeferenced data.
              </p>
            </div>
          </div>
        </div>
      </section>
      <section className="section">
        <div className="container">
          <h1 className="title">Explore</h1>
          <h2 className="subtitle">
            Click on the name of a city to explore the map.
          </h2>
          <CityList prefix="/en" items={cities} />
        </div>
      </section>
      <section className="section">
        <div className="container">
          <h1 className="title">Data</h1>
          <div className="content">
            <p>
              You can access the data presented on the map, both the vector
              layer of the detected settlements, as well as other analytical
              data generated, grouped by city and by last updated time.
            </p>
            <Link className="button is-primary" to="/en/data">
              Download Data
            </Link>
          </div>
        </div>
      </section>
      <section className="section">
        <div className="container">
          <h1 className="title">Publications</h1>
          <div className="content">
            <p>
              You can download and read publications about the detection
              methodology.
            </p>
            <Link className="button is-primary" to="/en/publications">
              See Publications
            </Link>
          </div>
        </div>
      </section>
      <section className="section">
        <div className="container">
          <h1 className="title">On Press</h1>
          <div className="content">
            <NewsList items={data.site.siteMetadata.press} />
          </div>
        </div>
      </section>
      <section className="section">
        <div className="container">
          <h1 className="title">With support of</h1>
          <div className="has-text-centered">
            <ul className="sponsors">
              <li>
                <a href="https://www.mapbox.com">
                  <img src={mapboxLogo} alt="Mapbox" />
                </a>
              </li>
            </ul>
          </div>
        </div>
      </section>
      <section className="section">
        <div className="container">
          <h1 className="title">License</h1>
          <div className="content">
            <p>
              Data is made available made available under the{' '}
              <strong>Public Domain Dedication and License version 1.0</strong>,
              from Open Data Commons.<br /> You are free to copy, distribute and
              use the data, produce new publications based on them, and modify
              and transform it.
            </p>
            <a
              className="button is-primary"
              href="https://opendatacommons.org/licenses/pddl/"
              target="_blank"
            >
              Read License
            </a>
          </div>
        </div>
      </section>
      <section className="section">
        <div className="container">
          <h1 className="title">Contact</h1>
          <div className="content">
            <p>
              If you have any question about our methodology or data, contact us
              via <a href="mailto:contacto@dymaxionalabs.com">e-mail</a>
            </p>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  )
}

export const query = graphql`
  query IndexEnQuery {
    ...IndexFragment
  }
`

export default IndexPage
