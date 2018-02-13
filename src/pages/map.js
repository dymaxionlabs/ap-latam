import React from 'react'

const Map = props => (
  <div id="map"></div>
)

const MapPage = ({ data }) => (
  <Map />
)

export const query = graphql`
  query MapQuery {
    allCitiesJson {
      edges {
        node {
          name
          country
          path
          center {
            lat
            lon
          }
          zoom
        }
      }
    }
  }
`

export default MapPage
