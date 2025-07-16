import { apiDev } from './api';

export interface ScrapedFile {
  id: string;
  baseId: string;
  url: string;
  pageTitle: string;
  isExcluded: boolean;
  status: 'done' | 'cleaning' | 'notFound' | 'error';
  lastScrapedAt: string;
  sourceId: string;
  createdAt: string;
  updatedAt: string;
}

export interface ApiResponse {
  response: any;
}

export interface ScrapedFilesListResponse {
  data: ScrapedFile[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface ScrapedFilesListParams {
  sourceId?: string;
  isExcluded?: boolean;
  page?: number;
  pageSize?: number;
  sorting?: string;
}

// Get all scraped files with optional filtering
export const getScrapedFiles = async (
  params: ScrapedFilesListParams = {}
): Promise<ScrapedFilesListResponse> => {
  const response = await apiDev.get(`/source-file/scraped/all`, {
    params: {
      sourceId: params.sourceId,
      isExcluded: params.isExcluded,
      page: params.page || 1,
      pageSize: params.pageSize || 10,
      sorting: params.sorting || 'last_scraped_at desc',
    },
  });

  const apiResponse: ApiResponse = response.data;

  // Transform the API response to match our expected structure
  const files = apiResponse.response || [];
  const firstItem = files[0];

  return {
    data: files,
    total: firstItem?.total || files.length,
    page: parseInt(firstItem?.page || '1'),
    pageSize: params.pageSize || 10,
    totalPages: firstItem?.totalPages || 1,
  };
};

// Update exclusion status of a scraped file
export const updateFileExclusion = async (
  fileId: string,
  isExcluded: boolean
): Promise<ScrapedFile> => {
  const response = await apiDev.post('/source-file/exclude', {
    baseId: fileId,
    excluded: isExcluded,
  });

  const apiResponse: ApiResponse = response.data;
  return apiResponse.response?.[0] || apiResponse.response;
};

// Refresh/re-scrape a specific file
export const refreshScrapedFile = async (fileId: string): Promise<void> => {
  await apiDev.post('/source-file/refresh', {
    fileId: fileId,
  });
};

// Delete a file
export const deleteFile = async (fileId: string): Promise<void> => {
  await apiDev.post('/source-file/remove', {
    baseId: fileId,
  });
};

// Get raw content of a scraped file
export const getFileRawContent = async (fileId: string): Promise<string> => {
  const response = await apiDev.get('/source-file/content/raw', {
    params: { fileId },
  });
  return response.data.response;
};

// Get cleaned content of a scraped file
export const getFileCleanedContent = async (
  fileId: string
): Promise<string> => {
  const response = await apiDev.get('/source-file/content/cleaned', {
    params: { fileId },
  });
  return response.data.response;
};

// Get edited content of a scraped file
export const getFileEditedContent = async (fileId: string): Promise<string> => {
  const response = await apiDev.get('/source-file/content/edited', {
    params: { fileId },
  });
  return response.data.response;
};

// Update edited content of a scraped file
export const updateFileEditedContent = async (
  fileId: string,
  content: string
): Promise<void> => {
  await apiDev.post('/source-file/content/update-edited', {
    fileId: fileId,
    content: content,
  });
};
