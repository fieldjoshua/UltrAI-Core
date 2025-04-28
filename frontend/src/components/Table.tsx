import React from 'react';

interface Column {
  id: string;
  header: string;
  accessor: (row: Record<string, unknown>) => React.ReactNode;
  sortable?: boolean;
}

interface TableProps {
  columns: Column[];
  data: Record<string, unknown>[];
  sortColumn?: string;
  sortDirection?: 'asc' | 'desc';
  onSort?: (columnId: string) => void;
  ariaLabel?: string;
  ariaDescribedBy?: string;
}

export const Table: React.FC<TableProps> = ({
  columns,
  data,
  sortColumn,
  sortDirection,
  onSort,
  ariaLabel,
  ariaDescribedBy,
}) => {
  const handleKeyDown = (e: React.KeyboardEvent, columnId: string) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onSort?.(columnId);
    }
  };

  return (
    <div className="overflow-x-auto">
      <table
        aria-label={ariaLabel}
        aria-describedby={ariaDescribedBy}
        className="min-w-full divide-y divide-gray-200"
      >
        <thead className="bg-gray-50">
          <tr>
            {columns.map(column => (
              <th
                key={column.id}
                scope="col"
                tabIndex={column.sortable ? 0 : undefined}
                onKeyDown={e => handleKeyDown(e, column.id)}
                onClick={() => {
                  if (column.sortable) {
                    onSort?.(column.id);
                  }
                }}
                className={`px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider ${
                  column.sortable
                    ? 'cursor-pointer hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
                    : ''
                }`}
                aria-sort={
                  column.id === sortColumn
                    ? sortDirection === 'asc'
                      ? 'ascending'
                      : 'descending'
                    : undefined
                }
              >
                <div className="flex items-center space-x-1">
                  <span>{column.header}</span>
                  {column.sortable && (
                    <span className="ml-1" aria-hidden="true">
                      {column.id === sortColumn
                        ? sortDirection === 'asc'
                          ? '↑'
                          : '↓'
                        : '↕'}
                    </span>
                  )}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {data.map((row, rowIndex) => (
            <tr key={rowIndex} className="hover:bg-gray-50">
              {columns.map(column => (
                <td
                  key={column.id}
                  className="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                >
                  {column.accessor(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
