import { FC, useState, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { MdOutlineEdit, MdRefresh, MdOutlineStopCircle } from 'react-icons/md';
import { Button, Card, DataTable, Icon, Track } from 'components';
import {
  ColumnDef,
  PaginationState,
  SortingState,
  ColumnFiltersState,
} from '@tanstack/react-table';
import { useToast } from 'hooks/useToast';
import { Link } from 'react-router-dom';
import 'pages/Agency/AgencyList.scss';

// Mock data types
interface ApiIntegration {
  id: string;
  baseId: string;
  name: string;
  lastScraped: string;
  status: 'running' | 'done';
}

// Mock data
const mockApiData: ApiIntegration[] = [
  {
    id: '1',
    baseId: 'arva-123',
    name: 'ARVA',
    lastScraped: '2024-05-06T10:08:00Z',
    status: 'running',
  },
  {
    id: '2',
    baseId: 'riigiteataja-456',
    name: 'Riigiteataja',
    lastScraped: '2024-05-06T10:08:00Z',
    status: 'done',
  },
  // Add more mock data to reach 170 results
  ...Array.from({ length: 168 }, (_, i) => ({
    id: `${i + 3}`,
    baseId: `api-${i + 3}`,
    name: `API Integration ${i + 3}`,
    lastScraped: '2024-05-06T10:08:00Z',
    status: (i % 2 === 0 ? 'running' : 'done') as 'running' | 'done',
  })),
];

const ApiList: FC = () => {
  const { t } = useTranslation();
  const toast = useToast();

  const [isRefreshing, setIsRefreshing] = useState<string | null>(null);
  const [isStopping, setIsStopping] = useState<string | null>(null);

  // Table state for client-side pagination and sorting
  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 10,
  });
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);

  // Mock API calls
  const handleStopScraping = async (apiId: string) => {
    setIsStopping(apiId);
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1000));

    toast.open({
      type: 'success',
      title: t('global.notification'),
      message: t('knowledgeBase.stopSuccess'),
    });

    setIsStopping(null);
  };

  const handleRefreshApi = async (apiId: string) => {
    setIsRefreshing(apiId);
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1000));

    toast.open({
      type: 'success',
      title: t('global.notification'),
      message: t('knowledgeBase.refreshSuccess'),
    });

    setIsRefreshing(null);
  };

  // Process data for table (sorting, filtering, pagination)
  const processedData = useMemo(() => {
    let filteredData = [...mockApiData];

    // Apply column filters
    columnFilters.forEach((filter) => {
      if (filter.value) {
        filteredData = filteredData.filter((item) =>
          String(item[filter.id as keyof ApiIntegration])
            .toLowerCase()
            .includes(String(filter.value).toLowerCase())
        );
      }
    });

    // Apply sorting
    if (sorting.length > 0) {
      const sort = sorting[0];
      filteredData.sort((a, b) => {
        const aValue = a[sort.id as keyof ApiIntegration];
        const bValue = b[sort.id as keyof ApiIntegration];

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
  }, [mockApiData, pagination, sorting, columnFilters]);

  const columns: ColumnDef<ApiIntegration>[] = [
    {
      accessorKey: 'name',
      header: t('global.name'),
      enableColumnFilter: false,
      cell: ({ row }) => (
        <Link
          to={`/api/${row.original.baseId}`}
          style={{ textDecoration: 'underline', color: '#005AA3' }}
        >
          <div className="agencies__agency-cell">{row.original.name}</div>
        </Link>
      ),
    },
    {
      accessorKey: 'lastScraped',
      header: t('knowledgeBase.lastScraped'),
      enableColumnFilter: false,
      cell: ({ row }) => (
        <span>
          {new Date(row.original.lastScraped).toLocaleDateString('et-EE', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
          })}{' '}
          {new Date(row.original.lastScraped).toLocaleTimeString('et-EE', {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </span>
      ),
    },
    {
      accessorKey: 'status',
      header: t('global.status'),
      cell: ({ row }) => {
        const statusMap = {
          running: 'In progress',
          done: 'Done',
        };

        const statusColorMap = {
          running: '#005AA3',
          done: '#266B42',
        };

        return (
          <span
            className="agencies__status-cell"
            style={{
              color: statusColorMap[row.original.status],
              borderColor: statusColorMap[row.original.status],
            }}
          >
            {statusMap[row.original.status]}
          </span>
        );
      },
      enableColumnFilter: false,
    },
    {
      id: 'actions',
      header: '',
      cell: ({ row }) => (
        <Track gap={32} justify="end">
          {row.original.status === 'running' ? (
            <Button
              className="agencies__action-btn"
              appearance="text"
              size="s"
              onClick={() => handleStopScraping(row.original.id)}
              disabled={isStopping === row.original.id}
            >
              <Icon
                icon={<MdOutlineStopCircle fontSize={20} />}
                size="medium"
              />
              {t('global.stop')}
            </Button>
          ) : (
            <Button
              className="agencies__action-btn"
              appearance="text"
              size="s"
              onClick={() => handleRefreshApi(row.original.id)}
              disabled={isRefreshing === row.original.id}
            >
              <Icon icon={<MdRefresh fontSize={20} />} size="medium" />
              {t('knowledgeBase.refresh')}
            </Button>
          )}

          <Link
            style={{ display: 'flex', textDecoration: 'none' }}
            to={`/api/${row.original.baseId}/schedule`}
          >
            <Button
              disabled={row.original.status === 'running'}
              appearance="text"
              className="agencies__action-btn"
            >
              <Icon icon={<MdOutlineEdit fontSize={20} />} size="medium" />
              {t('knowledgeBase.scrapeInterval')}
            </Button>
          </Link>

          <Button
            disabled={row.original.status === 'running'}
            appearance="text"
            className="agencies__action-btn"
          >
            <Icon icon={<MdOutlineEdit fontSize={20} />} size="medium" />
            {t('global.edit')}
          </Button>
        </Track>
      ),
    },
  ];

  return (
    <div className="agencies">
      <Track
        style={{ marginBottom: 16, minWidth: 800 }}
        justify="between"
        align="center"
      >
        <h1 className="h1">{t('menu.apiIntegrations')}</h1>
      </Track>

      <Card>
        <DataTable
          data={processedData.data}
          columns={columns}
          pagination={pagination}
          setPagination={setPagination}
          sorting={sorting}
          setSorting={setSorting}
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

export default ApiList;
