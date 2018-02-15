import React from 'react'
import PropTypes from 'prop-types'
import Helmet from 'react-helmet'

import NavBar from '../components/navbar'
import './index.sass'

const TemplateWrapper = ({ children, data }) => (
  <div>
    <Helmet
      title={data.site.siteMetadata.title}
      meta={[
        {
          name: 'description',
          content:
            'El mapa está elaborado a partir de la aplicación de técnicas de machine learning en imágenes satelitales y otros datos georreferenciados.',
        },
      ]}
    />
    <div>
      <NavBar name={data.site.siteMetadata.name} />
      {children()}
    </div>
  </div>
)

export const query = graphql`
  query LayoutQuery {
    site {
      siteMetadata {
        name
        title
      }
    }
  }
`

TemplateWrapper.propTypes = {
  children: PropTypes.func,
}

export default TemplateWrapper
