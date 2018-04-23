import React from 'react'

export const layoutFragment = graphql`
  fragment LayoutFragment on RootQueryType {
    site {
      siteMetadata {
        name
        title
        meta {
          description
        }
      }
    }
  }
`
