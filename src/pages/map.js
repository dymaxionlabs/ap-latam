import React from 'react'
import ReactMapGL from 'react-map-gl'
import css from './map.sass'
import queryString from 'query-string'

class Map extends React.Component {
  constructor(props) {
    super(props)

    this.state = {
      viewport: {
        latitude: this.props.lat,
        longitude: this.props.lon,
        zoom: this.props.zoom,
      },
    }

    if (typeof window !== 'undefined') {
      this.state.width = window.innerWidth
      this.state.height = window.innerHeight
    }
  }

  componentDidMount() {
    window.addEventListener('resize', this._resize)
    this._resize()
  }

  componentWillUnmount() {
    window.removeEventListener('resize', this._resize)
  }

  _onViewportChange = viewport =>
    this.setState({
      viewport: { ...this.state.viewport, ...viewport },
    })

  _resize = () =>
    this._onViewportChange({
      width: this.props.width || window.innerWidth,
      height: this.props.height || window.innerHeight,
    })

  render() {
    const { viewport, settings } = this.state
    return (
      <ReactMapGL
        {...viewport}
        {...settings}
        id="map"
        mapStyle="mapbox://styles/munshkr/cjdng40dl08ie2rocx25qe8zh"
        onViewportChange={this._onViewportChange}
      />
    )
  }
}

const MapPage = ({ data }) => {
  let cityId = null
  if (typeof window !== 'undefined') {
    const parsedHash = queryString.parse(window.location.search)
    cityId = parsedHash.id
  }

  const cityEdge =
    data.allCitiesJson.edges.find(e => e.node.internalId === cityId) ||
    data.allCitiesJson.edges[0]
  const city = cityEdge.node

  return <Map zoom={city.zoom} lat={city.center.lat} lon={city.center.lon} />
}

export const query = graphql`
  query MapQuery {
    allCitiesJson {
      edges {
        node {
          internalId
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
