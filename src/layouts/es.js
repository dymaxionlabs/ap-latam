import React from 'react'
import PropTypes from 'prop-types'
import Helmet from 'react-helmet'

import {NavBar, NavBarItem} from '../components/navbar'
import './index.sass'

const TemplateWrapper = ({ children, data }) => (
  <div>
    <Helmet
      title={data.site.siteMetadata.title}
      meta={[
        {
          name: 'description',
          content: data.site.siteMetadata.meta.description,
        },
      ]}
    />
    <div>
      <NavBar basepath="/es" name={data.site.siteMetadata.name}>
        <NavBarItem name="Mapa" url="/es/map" />
        <NavBarItem name="Datos" url="/es/data" />
        <NavBarItem name="Publicaciones" url="/es/publications" />
        <NavBarItem name="Contacto" url="/es/contact" />
      </NavBar>

      {children()}
    </div>
  </div>
)

export const query = graphql`
  query LayoutEsQuery {
    ...LayoutFragment
  }
`

TemplateWrapper.propTypes = {
  children: PropTypes.func,
}

export default TemplateWrapper
