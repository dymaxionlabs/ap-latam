export default from './_map'

export const mapEsQuery = graphql`
  query MapEsQuery {
    ...MapFragment
  }
`
