import { action, observable } from 'mobx';

import BaseStore from 'models/base_store';
import { MatrixUserIdentity } from 'models/matrix/matrix.types';

import { RootStore } from 'state';

export class MatrixStore extends BaseStore {
  @observable.shallow
  matrixUserIdentity?: MatrixUserIdentity;

  @observable.shallow
  items: { [pk: string]: MatrixUserIdentity } = {};

  constructor(rootStore: RootStore) {
    super(rootStore);

    this.path = '/matrix_user_identities/'
  }

  @action
  async createMatrixUserIdentity(data: any) {
    const identity = await this.create(data);

    this.items = {
      ...this.items,
      [identity.id]: identity,
    };

    return identity;
  }

  @action
  async updateMatrixUserIdentity(id, data: Partial<MatrixUserIdentity>) {
   const identity: MatrixUserIdentity = await super.update(id, data);

    this.items = {
      ...this.items,
      [identity.id]: identity,
    };
  }


}