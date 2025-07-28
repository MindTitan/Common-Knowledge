import { FC, useState, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import {
  MdRefresh,
  MdOutlineViewColumn,
  MdOutlineTableChart,
  MdGridView,
} from 'react-icons/md';
import {
  Button,
  Card,
  DataTable,
  FormInput,
  Icon,
  Track,
  SwitchBox,
  Tooltip,
} from 'components';
import {
  ColumnDef,
  PaginationState,
  SortingState,
  ColumnFiltersState,
} from '@tanstack/react-table';
import { useToast } from 'hooks/useToast';
import 'pages/Agency/AgencyList.scss';

// Mock data types
interface ApiSource {
  id: string;
  baseId: string;
  name: string;
  status: 'new' | 'done' | 'cleaning' | 'not_found';
  excluded: boolean;
  scraped: string;
}

interface FormData {
  search: string;
}

// Mock API detail data
const mockApiDetail = {
  name: 'ARVA',
};

// Mock sources data
const mockSourcesData: ApiSource[] = [
  {
    id: '001',
    baseId: 'source-001',
    name: 'New',
    status: 'new',
    excluded: false,
    scraped: '2024-05-06T10:08:00Z',
  },
  {
    id: '002',
    baseId: 'source-002',
    name: 'Eraisik',
    status: 'done',
    excluded: true,
    scraped: '2024-05-06T10:08:00Z',
  },
  {
    id: '003',
    baseId: 'source-003',
    name: 'Ettevõte',
    status: 'cleaning',
    excluded: true,
    scraped: '2024-05-06T10:08:00Z',
  },
  {
    id: '004',
    baseId: 'source-004',
    name: 'Kontakt',
    status: 'not_found',
    excluded: true,
    scraped: '2024-05-06T10:08:00Z',
  },
  // Add more mock data to reach 170 results
  ...Array.from({ length: 166 }, (_, i) => ({
    id: `${i + 5}`.padStart(3, '0'),
    baseId: `source-${i + 5}`,
    name: `Source ${i + 5}`,
    status: ['new', 'done', 'cleaning', 'not_found'][i % 4] as
      | 'new'
      | 'done'
      | 'cleaning'
      | 'not_found',
    excluded: i % 2 === 1,
    scraped: '2024-05-06T10:08:00Z',
  })),
];

const ApiDetail: FC = () => {
  const { t } = useTranslation();
  const toast = useToast();
  const { id: apiId } = useParams<{ id: string }>();

  const [formData, setFormData] = useState<FormData>({
    search: '',
  });
  const [searchQuery, setSearchQuery] = useState('');

  // Table state for server-side pagination and sorting
  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 10,
  });
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);

  // Handle search input change
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData((prev) => ({ ...prev, search: e.target.value }));
  };

  // Handle search button click
  const handleSearchSubmit = () => {
    setSearchQuery(formData.search);
    setPagination((prev) => ({ ...prev, pageIndex: 0 }));
  };

  // Handle Enter key in search input
  const handleSearchKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSearchSubmit();
    }
  };

  // Convert sorting state to API format
  const getSortingParam = (sorting: SortingState): string => {
    if (sorting.length === 0) return 'id asc';

    const sort = sorting[0];
    let field = sort.id;

    // Map column IDs to API field names
    const fieldMap: Record<string, string> = {
      id: 'id',
      name: 'name',
      excluded: 'excluded',
      status: 'status',
      scraped: 'scraped',
    };

    field = fieldMap[field] || field;
    return `${field} ${sort.desc ? 'desc' : 'asc'}`;
  };

  // Mock API calls
  const handleRefreshSource = async (sourceId: string) => {
    await new Promise((resolve) => setTimeout(resolve, 1000));

    toast.open({
      type: 'success',
      title: t('global.notification'),
      message: t('knowledgeBase.refreshSuccess'),
    });
  };

  const handleToggleExcluded = async (sourceId: string, excluded: boolean) => {
    await new Promise((resolve) => setTimeout(resolve, 500));

    toast.open({
      type: 'success',
      title: t('global.notification'),
      message: t('knowledgeBase.updateSuccess'),
    });
  };

  const handleViewContent = async (
    source: ApiSource,
    type: 'raw' | 'cleaned' | 'edited'
  ) => {
    toast.open({
      type: 'info',
      title: t('global.notification'),
      message: `Viewing ${type} content for ${source.name}`,
    });
  };

  const handlePaginationChange = (newPagination: PaginationState) => {
    setPagination(newPagination);
  };

  const handleSortingChange = (newSorting: SortingState) => {
    setSorting(newSorting);
  };

  // Process data for table
  const processedData = useMemo(() => {
    let filteredData = [...mockSourcesData];

    // Apply search filter
    if (searchQuery.trim()) {
      filteredData = filteredData.filter(
        (item) =>
          item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          item.id.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Apply column filters
    columnFilters.forEach((filter) => {
      if (filter.value) {
        filteredData = filteredData.filter((item) =>
          String(item[filter.id as keyof ApiSource])
            .toLowerCase()
            .includes(String(filter.value).toLowerCase())
        );
      }
    });

    // Apply sorting
    if (sorting.length > 0) {
      const sort = sorting[0];
      filteredData.sort((a, b) => {
        const aValue = a[sort.id as keyof ApiSource];
        const bValue = b[sort.id as keyof ApiSource];

        if (aValue < bValue) return sort.desc ? 1 : -1;
        if (aValue > bValue) return sort.desc ? -1 : 1;
        return 0;
      });
    }

    // Calculate pagination
    const startIndex = pagination.pageIndex * pagination.pageSize;
    const endIndex = startIndex + pagination.pageSize;
    const paginatedData = filteredData.slice(startIndex, endIndex);

    return {
      data: paginatedData,
      total: filteredData.length,
      totalPages: Math.ceil(filteredData.length / pagination.pageSize),
    };
  }, [mockSourcesData, searchQuery, pagination, sorting, columnFilters]);

  const getStatusStyle = (status: string) => {
    const statusMap = {
      new: { color: '#005AA3', text: 'New' },
      done: { color: '#266B42', text: 'Done' },
      cleaning: { color: '#FF9800', text: 'Cleaning' },
      not_found: { color: '#D32F2F', text: 'Not found' },
    };

    return statusMap[status as keyof typeof statusMap] || statusMap.new;
  };

  const columns: ColumnDef<ApiSource>[] = [
    {
      accessorKey: 'id',
      header: t('knowledgeBase.id'),
      enableColumnFilter: false,
      cell: ({ row }) => (
        <Tooltip content={row.original.id}>
          <div
            style={{
              maxWidth: 100,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
            }}
            className="agencies__agency-cell"
          >
            {row.original.id}
          </div>
        </Tooltip>
      ),
    },
    {
      accessorKey: 'name',
      header: t('global.name'),
      enableColumnFilter: false,
      cell: ({ row }) => (
        <Tooltip content={row.original.name}>
          <div
            style={{
              maxWidth: 200,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
            }}
            className="agencies__agency-cell"
          >
            {row.original.name}
          </div>
        </Tooltip>
      ),
    },
    {
      id: 'actions',
      header: '',
      cell: ({ row }) => (
        <Track
          justify="start"
          align="flex-start"
          gap={16}
          style={{ width: 'max-content' }}
        >
          <Button
            appearance="text"
            className="agencies__action-btn"
            size="s"
            onClick={() => handleRefreshSource(row.original.id)}
            style={{ color: '#005AA3', padding: '4px 8px' }}
          >
            <Icon icon={<MdRefresh fontSize={16} />} size="small" />
            {t('knowledgeBase.refresh')}
          </Button>

          <Button
            appearance="text"
            className="agencies__action-btn"
            size="s"
            onClick={() => handleViewContent(row.original, 'raw')}
            style={{ color: '#005AA3', padding: '4px 8px' }}
          >
            <Icon icon={<MdOutlineViewColumn fontSize={16} />} size="small" />
            Raw
          </Button>

          <Button
            appearance="text"
            className="agencies__action-btn"
            size="s"
            onClick={() => handleViewContent(row.original, 'cleaned')}
            style={{ color: '#005AA3', padding: '4px 8px' }}
          >
            <Icon icon={<MdOutlineTableChart fontSize={16} />} size="small" />
            {t('knowledgeBase.cleaned')}
          </Button>

          <Button
            appearance="text"
            className="agencies__action-btn"
            size="s"
            disabled
            style={{ color: '#C0C2C9', padding: '4px 8px' }}
          >
            <Icon icon={<MdGridView fontSize={16} />} size="small" />
            {t('knowledgeBase.edited')}
          </Button>
        </Track>
      ),
    },
    {
      accessorKey: 'excluded',
      id: 'excluded',
      enableColumnFilter: false,
      header: t('knowledgeBase.excluded'),
      cell: ({ row }) => (
        <SwitchBox
          label=""
          checked={row.original.excluded}
          onCheckedChange={(checked) =>
            handleToggleExcluded(row.original.id, checked)
          }
        />
      ),
    },
    {
      accessorKey: 'status',
      header: t('global.status'),
      enableColumnFilter: false,
      cell: ({ row }) => {
        const statusStyle = getStatusStyle(row.original.status);
        return (
          <span
            className="agencies__status-cell"
            style={{
              color: statusStyle.color,
              borderColor: statusStyle.color,
            }}
          >
            {statusStyle.text}
          </span>
        );
      },
    },
    {
      accessorKey: 'scraped',
      header: t('knowledgeBase.scraped'),
      enableColumnFilter: false,
      cell: ({ row }) => (
        <span>
          {new Date(row.original.scraped).toLocaleDateString('et-EE', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
          })}{' '}
          {new Date(row.original.scraped).toLocaleTimeString('et-EE', {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </span>
      ),
    },
  ];

  return (
    <div className="agencies">
      <Track
        style={{ marginBottom: 16, width: '100%' }}
        justify="between"
        align="center"
      >
        <div>
          <span className="agencies__agency">{mockApiDetail.name}</span>
        </div>
      </Track>

      <Card
        header={
          <Track gap={16} justify="end" align="center">
            <FormInput
              className="agencies__search"
              label={t('knowledgeBase.searchWithinListedSources')}
              name="search"
              value={formData.search}
              onChange={handleSearchChange}
              onKeyPress={handleSearchKeyPress}
            />
            <Button appearance="primary" onClick={handleSearchSubmit}>
              {t('global.search')}
            </Button>
          </Track>
        }
      >
        <DataTable
          data={processedData.data}
          columns={columns}
          pagination={pagination}
          setPagination={handlePaginationChange}
          sorting={sorting}
          setSorting={handleSortingChange}
          columnFilters={columnFilters}
          setFiltering={setColumnFilters}
          sortable
          filterable
          pagesCount={processedData.totalPages}
          isClientSide={true}
        />

        <div className="agencies__footer">
          <span className="agencies__total">
            {processedData.total} {t('knowledgeBase.results')}
          </span>
        </div>
      </Card>
    </div>
  );
};

export default ApiDetail;
