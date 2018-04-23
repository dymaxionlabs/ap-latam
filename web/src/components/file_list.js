import React from 'react'

const FileListItem = props => {
  const filename = props.node.relativePath.split('/')[1]
  return (
    <li>
      <a href={props.node.publicURL} download={filename}>
        {props.node.relativePath}
      </a>
    </li>
  )
}

const FileList = props => (
  <ul>{props.files.map(node => <FileListItem key={node.publicURL} node={node} />)}</ul>
)

export default { FileList, FileListItem }
