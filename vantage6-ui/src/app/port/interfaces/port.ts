import { Resource } from 'src/app/shared/enum';

// TODO include result?
export interface Port {
  id: number;
  type: string;
  port: number;
  label: string;
  result_id: number; // TODO necessary?
}
