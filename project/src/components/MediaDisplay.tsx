import React, { useState } from 'react';
import { FileVideo, Download, X, ChevronLeft, ChevronRight, Image as ImageIcon } from 'lucide-react';

interface Attachment {
  id: string;
  file_url: string;
  file_name: string;
  file_type: string;
  purpose: string;
  uploaded_at: string;
}

interface MediaDisplayProps {
  attachments: Attachment[];
  title?: string;
}

const MediaDisplay: React.FC<MediaDisplayProps> = ({ attachments, title = "Media Attachments" }) => {
  const [selectedMedia, setSelectedMedia] = useState<Attachment | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [imageErrors, setImageErrors] = useState<Set<string>>(new Set());

  if (!attachments || attachments.length === 0) {
    return null;
  }

  const openMediaModal = (attachment: Attachment) => {
    const index = attachments.findIndex(att => att.id === attachment.id);
    setCurrentIndex(index);
    setSelectedMedia(attachment);
  };

  const closeMediaModal = () => {
    setSelectedMedia(null);
  };

  const nextMedia = () => {
    const nextIndex = (currentIndex + 1) % attachments.length;
    setCurrentIndex(nextIndex);
    setSelectedMedia(attachments[nextIndex]);
  };

  const prevMedia = () => {
    const prevIndex = (currentIndex - 1 + attachments.length) % attachments.length;
    setCurrentIndex(prevIndex);
    setSelectedMedia(attachments[prevIndex]);
  };

  const downloadFile = (attachment: Attachment) => {
    const link = document.createElement('a');
    link.href = attachment.file_url;
    link.download = attachment.file_name || 'download';
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleImageError = (attachmentId: string) => {
    setImageErrors(prev => new Set(prev).add(attachmentId));
  };

  const getFileUrl = (attachment: Attachment) => {
    // Ensure the URL is properly formatted
    let url = attachment.file_url;
    if (url && !url.startsWith('http') && !url.startsWith('/')) {
      // If it's a relative path, make it absolute
      url = `http://127.0.0.1:8000${url.startsWith('/') ? '' : '/'}${url}`;
    }
    return url;
  };

  return (
    <>
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
        
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {attachments.map((attachment) => {
            const fileUrl = getFileUrl(attachment);
            const hasImageError = imageErrors.has(attachment.id);
            
            return (
              <div key={attachment.id} className="group">
                <div 
                  className="aspect-square bg-gray-100 rounded-lg overflow-hidden cursor-pointer hover:bg-gray-200 transition-colors relative border-2 border-gray-200 hover:border-blue-300"
                  onClick={() => openMediaModal(attachment)}
                >
                  {attachment.file_type === 'image' && !hasImageError ? (
                    <div className="relative w-full h-full">
                      <img
                        src={fileUrl}
                        alt={attachment.file_name}
                        className="w-full h-full object-cover"
                        onError={() => handleImageError(attachment.id)}
                        loading="lazy"
                      />
                      <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all flex items-center justify-center">
                        <ImageIcon className="h-8 w-8 text-white opacity-0 group-hover:opacity-100 transition-opacity" />
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-center justify-center h-full">
                      <div className="text-center">
                        {attachment.file_type === 'video' ? (
                          <FileVideo className="h-8 w-8 text-blue-500 mx-auto mb-2" />
                        ) : (
                          <ImageIcon className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                        )}
                        <p className="text-xs text-gray-500 font-medium">
                          {attachment.file_type === 'video' ? 'Video' : 'Image'}
                        </p>
                      </div>
                    </div>
                  )}
                </div>

                <div className="mt-2 flex items-center justify-between">
                  <p className="text-xs text-gray-500 truncate flex-1 mr-2" title={attachment.file_name}>
                    {attachment.file_name}
                  </p>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      downloadFile(attachment);
                    }}
                    className="text-gray-400 hover:text-blue-600 transition-colors p-1"
                    title="Download"
                  >
                    <Download className="h-4 w-4" />
                  </button>
                </div>

                {attachment.purpose && attachment.purpose !== 'other' && (
                  <span className="inline-block mt-1 px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
                    {attachment.purpose.replace('_', ' ')}
                  </span>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Enhanced Modal with Carousel */}
      {selectedMedia && (
        <div className="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50 p-4">
          <div className="relative max-w-4xl max-h-full w-full h-full flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between p-4 text-white">
              <div className="flex items-center gap-4">
                <h3 className="text-lg font-semibold">
                  {selectedMedia.file_name}
                </h3>
                <span className="text-sm text-gray-300">
                  {currentIndex + 1} of {attachments.length}
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => downloadFile(selectedMedia)}
                  className="p-2 text-white hover:text-gray-300 transition-colors rounded-lg hover:bg-white hover:bg-opacity-20"
                  title="Download"
                >
                  <Download className="h-5 w-5" />
                </button>
                <button
                  onClick={closeMediaModal}
                  className="p-2 text-white hover:text-gray-300 transition-colors rounded-lg hover:bg-white hover:bg-opacity-20"
                  title="Close"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            </div>

            {/* Media Content */}
            <div className="flex-1 flex items-center justify-center">
              {selectedMedia.file_type === 'image' ? (
                <img
                  src={getFileUrl(selectedMedia)}
                  alt={selectedMedia.file_name}
                  className="max-w-full max-h-full object-contain"
                  onError={(e) => {
                    const target = e.target as HTMLImageElement;
                    target.style.display = 'none';
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'text-center py-8 text-white';
                    errorDiv.innerHTML = `
                      <div class="text-center">
                        <svg class="h-16 w-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                        </svg>
                        <p class="text-gray-400">Image could not be loaded</p>
                        <p class="text-sm text-gray-500 mt-2">${selectedMedia.file_name}</p>
                      </div>
                    `;
                    target.parentElement?.appendChild(errorDiv);
                  }}
                />
              ) : (
                <video
                  src={getFileUrl(selectedMedia)}
                  controls
                  className="max-w-full max-h-full"
                >
                  Your browser does not support the video tag.
                </video>
              )}
            </div>

            {/* Navigation Arrows */}
            {attachments.length > 1 && (
              <>
                <button
                  onClick={prevMedia}
                  className="absolute left-4 top-1/2 transform -translate-y-1/2 p-3 bg-black bg-opacity-50 hover:bg-opacity-75 text-white rounded-lg transition-all"
                >
                  <ChevronLeft className="h-6 w-6" />
                </button>
                <button
                  onClick={nextMedia}
                  className="absolute right-4 top-1/2 transform -translate-y-1/2 p-3 bg-black bg-opacity-50 hover:bg-opacity-75 text-white rounded-lg transition-all"
                >
                  <ChevronRight className="h-6 w-6" />
                </button>
              </>
            )}

            {/* Thumbnail Navigation */}
            {attachments.length > 1 && (
              <div className="p-4">
                <div className="flex justify-center space-x-2 max-w-full overflow-x-auto">
                  {attachments.map((attachment, index) => (
                    <button
                      key={attachment.id}
                      onClick={() => {
                        setCurrentIndex(index);
                        setSelectedMedia(attachment);
                      }}
                      className={`flex-shrink-0 w-16 h-16 rounded-lg overflow-hidden border-2 transition-all ${
                        index === currentIndex ? 'border-white' : 'border-gray-600 hover:border-gray-400'
                      }`}
                    >
                      {attachment.file_type === 'image' ? (
                        <img
                          src={getFileUrl(attachment)}
                          alt={attachment.file_name}
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            const target = e.target as HTMLImageElement;
                            target.style.display = 'none';
                            const parent = target.parentElement!;
                            parent.innerHTML = `
                              <div class="w-full h-full bg-gray-700 flex items-center justify-center">
                                <svg class="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                                </svg>
                              </div>
                            `;
                          }}
                        />
                      ) : (
                        <div className="w-full h-full bg-gray-700 flex items-center justify-center">
                          <FileVideo className="h-6 w-6 text-gray-400" />
                        </div>
                      )}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
};

export default MediaDisplay; 