import React from 'react';
import './FilePreview.css';

const FilePreview = ({ files, onRemoveFile }) => {
  const getFileIcon = (file) => {
    const type = file.type;
    if (type.startsWith('image/')) return 'image';
    if (type.startsWith('video/')) return 'movie';
    if (type.startsWith('audio/')) return 'audiotrack';
    if (type.includes('pdf')) return 'picture_as_pdf';
    if (type.includes('word') || type.includes('document')) return 'description';
    if (type.includes('excel') || type.includes('spreadsheet')) return 'table_chart';
    if (type.includes('powerpoint') || type.includes('presentation')) return 'slideshow';
    if (type.includes('zip') || type.includes('rar')) return 'folder_zip';
    return 'insert_drive_file';
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const createThumbnail = (file) => {
    return new Promise((resolve) => {
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.readAsDataURL(file);
      } else {
        resolve(null);
      }
    });
  };

  if (!files || files.length === 0) return null;

  return (
    <div className="file-preview-container">
      <div className="file-preview-list">
        {files.map((file, index) => (
          <FileThumbnail
            key={`${file.name}-${index}`}
            file={file}
            index={index}
            onRemove={() => onRemoveFile(index)}
            getFileIcon={getFileIcon}
            formatFileSize={formatFileSize}
            createThumbnail={createThumbnail}
          />
        ))}
      </div>
    </div>
  );
};

const FileThumbnail = ({ file, index, onRemove, getFileIcon, formatFileSize, createThumbnail }) => {
  const [thumbnail, setThumbnail] = React.useState(null);

  React.useEffect(() => {
    createThumbnail(file).then(setThumbnail);
  }, [file, createThumbnail]);

  return (
    <div className="file-thumbnail">
      <div className="file-thumbnail-content">
        {thumbnail ? (
          <img src={thumbnail} alt={file.name} className="file-thumbnail-image" />
        ) : (
          <div className="file-thumbnail-icon">
            <span className="material-icons">{getFileIcon(file)}</span>
          </div>
        )}
        <div className="file-thumbnail-info">
          <div className="file-name" title={file.name}>
            {file.name.length > 15 ? `${file.name.substring(0, 15)}...` : file.name}
          </div>
          <div className="file-size">{formatFileSize(file.size)}</div>
        </div>
      </div>
      <button 
        className="remove-file-btn"
        onClick={onRemove}
        title="Remove file"
      >
        <span className="material-icons">close</span>
      </button>
    </div>
  );
};

export default FilePreview;
