import React from 'react'

export const dataFragment = graphql`
  fragment DataFragment on RootQueryType {
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
    allFile(
      sort: { fields: [relativePath], order: ASC }
      filter: { extension: { eq: "geojson" } }
    ) {
      edges {
        node {
          relativePath
          publicURL
          extension
        }
      }
    }
  }
`
