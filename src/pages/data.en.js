import React from 'react'
import Footer from '../components/footer'
import { FileList, FileListItem } from '../components/file_list'

const DataEnPage = ({ props, data }) => {
  const files = data.allFile.edges.map(e => e.node)
  return (
    <div>
      <section className="section">
        <div className="container">
          <h1 className="title">Data</h1>
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

export default DataEnPage
export const dataEnQuery = graphql`
  query DataEnQuery {
    ...DataFragment
  }
`
