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
      <NavBar prefix="/en" name={data.site.siteMetadata.name}>
        <NavBarItem name="Map" url="/en/map" />
        <NavBarItem name="Data" url="/en/data" />
        <NavBarItem name="Publications" url="/en/publications" />
        <NavBarItem name="Contact" url="/en/contact" />
      </NavBar>
      {children()}
    </div>
  </div>
)

export const query = graphql`
  query LayoutEnQuery {
    ...LayoutFragment
  }
`

TemplateWrapper.propTypes = {
  children: PropTypes.func,
}

export default TemplateWrapper
