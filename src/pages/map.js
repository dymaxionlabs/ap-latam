import React from 'react'
import ReactMapGL from 'react-map-gl'
import css from './map.sass'

class Map extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      viewport: {
        width: 400,
        height: 400,
        latitude: this.props.lat,
        longitude: this.props.lon,
        zoom: this.props.zoom
      }
    }
  }

  render() {
    return <ReactMapGL
      {...this.state.viewport}
      onViewportChange={(viewport) => this.setState({viewport})}
    />
  }
}

const MapPage = ({ data }) => {
  const cityName = 'Buenos Aires'
  const countryName = 'Argentina'
  const city = data.allCitiesJson.edges.find(e => e.node.name == cityName && e.node.country == countryName).node
  console.log(city)
  return <Map
    zoom={city.zoom}
    lat={city.center.lat}
    lon={city.center.lon}
  />
}

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
