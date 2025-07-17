// services/sources.ts
import { apiDev } from './api';

export interface Source {
  id: string;
  baseId: string;
  url: string;
  subsector: string;
  lastScrapedAt: string;
  status: string;
  agencyBaseId: string;
  createdAt: string;
  updatedAt: string;
  cronSchedule?: string;
  updateAutomatically?: boolean;
}

export interface ApiResponse {
  response: any;
}

export interface SourcesListResponse {
  data: Source[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface SourcesListParams {
  agencyBaseId: string;
  page?: number;
  pageSize?: number;
  sorting?: string;
}

export interface CreateSourceRequest {
  agencyBaseId: string;
  url?: string;
  subsector: string;
  type: 'file' | 'url' | 'api';
  files?: File[];
  apiUrl?: string;
}

export interface UpdateSourceSubsectorRequest {
  subsector: string;
}

// Get all sources for a specific agency
export const getSources = async (
  params: SourcesListParams
): Promise<SourcesListResponse> => {
  const response = await apiDev.get(`/source/all`, {
    params: {
      agencyBaseId: params.agencyBaseId,
      page: params.page || 1,
      pageSize: params.pageSize || 10,
      sorting: params.sorting || 'last_scraped_at desc',
    },
  });

  const apiResponse: ApiResponse = response.data;

  // Transform the API response to match our expected structure
  const sources = apiResponse.response || [];
  const firstItem = sources[0];

  return {
    data: sources,
    total: firstItem?.total,
    page: parseInt(firstItem?.page || '1'),
    pageSize: params.pageSize || 10,
    totalPages: firstItem?.totalPages || 1,
  };
};

// Create a new source (file upload)
export const createSourceFile = async (
  data: CreateSourceRequest
): Promise<Source> => {
  const formData = new FormData();
  formData.append('agencyBaseId', data.agencyBaseId);
  formData.append('subsector', data.subsector);
  formData.append('type', 'file');

  if (data.files) {
    data.files.forEach((file) => {
      formData.append('files', file);
    });
  }

  const response = await apiDev.post('/source/add', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  const apiResponse: ApiResponse = response.data;
  return apiResponse.response?.[0] || apiResponse.response;
};

// Create a new source (URL)
export const createSourceUrl = async (
  data: CreateSourceRequest
): Promise<Source> => {
  const response = await apiDev.post('/source/add', {
    agencyBaseId: data.agencyBaseId,
    url: data.url,
    subsector: data.subsector,
    type: 'url_to_scrape',
  });

  const apiResponse: ApiResponse = response.data;
  return apiResponse.response?.[0] || apiResponse.response;
};

// Create a new source (API)
export const createSourceApi = async (
  data: CreateSourceRequest
): Promise<Source> => {
  const response = await apiDev.post('/source/add', {
    agencyBaseId: data.agencyBaseId,
    apiUrl: data.apiUrl,
    subsector: data.subsector,
    type: 'api',
  });

  const apiResponse: ApiResponse = response.data;
  return apiResponse.response?.[0] || apiResponse.response;
};

// Update a source
export const updateSourceSubsector = async (
  sourceId: string,
  data: UpdateSourceSubsectorRequest
): Promise<Source> => {
  const response = await apiDev.post('/source/edit-subsector', {
    baseId: sourceId,
    subsector: data.subsector,
  });

  const apiResponse: ApiResponse = response.data;
  return apiResponse.response?.[0] || apiResponse.response;
};

// Delete a source
export const deleteSource = async (sourceId: string): Promise<void> => {
  await apiDev.post('/source/remove', {
    baseId: sourceId,
  });
};

// Stop scraping a source
export const stopSourceScraping = async (sourceId: string): Promise<void> => {
  await apiDev.post('/agency/sources/stop', {
    sourceId: sourceId,
  });
};

// Refresh/restart scraping a source
export const refreshSource = async (sourceId: string): Promise<void> => {
  await apiDev.post('/agency/sources/refresh', {
    sourceId: sourceId,
  });
};

// Get a specific source by baseId
export const getSource = async (baseId: string): Promise<Source> => {
  const response = await apiDev.get('/source/url/get', {
    params: {
      baseId: baseId,
    },
  });

  const apiResponse: ApiResponse = response.data;

  // Return the first source from the response array or the response itself
  return apiResponse.response?.[0] || apiResponse.response;
};

// Update source scrape interval
export const updateSourceScrapeInterval = async (
  sourceId: string,
  cronSchedule: string,
  updateAutomatically: boolean
): Promise<Source> => {
  const response = await apiDev.post('/source/edit-scrape-interval', {
    baseId: sourceId,
    cronSchedule: cronSchedule,
    updateAutomatically: updateAutomatically,
  });

  const apiResponse: ApiResponse = response.data;
  return apiResponse.response?.[0] || apiResponse.response;
};
