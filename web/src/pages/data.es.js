import React from 'react'
import Footer from './_footer.es'
import { FileList, FileListItem } from '../components/file_list'

const DataEsPage = ({ props, data }) => {
  const files = data.allFile.edges.map(e => e.node)
  return (
    <div>
      <section className="section">
        <div className="container">
          <h1 className="title">Datos</h1>
          <div className="content">
            <p />
            <FileList files={files} />
          </div>
        </div>
      </section>
      <Footer />
    </div>
  )
}

export default DataEsPage
export const dataEsQuery = graphql`
  query DataEsQuery {
    ...DataFragment
  }
`
