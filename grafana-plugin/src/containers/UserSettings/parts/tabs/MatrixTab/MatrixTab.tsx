import React, { HTMLAttributes, useCallback } from 'react';

import { HorizontalGroup, Icon, Input, Tooltip, VerticalGroup } from '@grafana/ui';
import cn from 'classnames/bind';
import { observer } from 'mobx-react';

import Text from 'components/Text/Text';
import { useStore } from 'state/useStore';
import { User } from 'models/user/user.types';

import styles from './MatrixTab.module.css';

const cx = cn.bind(styles);

interface MatrixInfoProps extends HTMLAttributes<HTMLElement> {
  userPk?: User['pk'];
}

export const MatrixInfo = observer((props: MatrixInfoProps) => {

  const userPk = props.userPk
  const store = useStore();
  const { userStore } = store;
  const { matrixStore } = store;

  const user = userStore.items[userPk];
  const user_matrix_identity = user.matrix_user_identity

  const getMatrixIdentityUserIdUpdateHandler = useCallback(
    async (event) => {
      const updated_matrix_user_id = event.target.value;
      console.log('Updated matrix.ts to use abstract method');

      var matrixUserIdPrimaryKey = user.matrix_user_identity;
      console.log('Current userId PrimaryKey is ' + matrixUserIdPrimaryKey);

      if (matrixUserIdPrimaryKey == null) {
        // User has no associated MatrixUserId - create one for them
        const createMatrixUserIdentityResponse = await userStore.createEmptyMatrixUserIdentity(user);
        console.log(createMatrixUserIdentityResponse);
        matrixUserIdPrimaryKey = createMatrixUserIdentityResponse.id
        console.log('primary key of new matrix_user_id is now ');
        console.log(matrixUserIdPrimaryKey);
      }

      await matrixStore.updateMatrixUserIdentity(matrixUserIdPrimaryKey, {
        user_id: updated_matrix_user_id,
        paging_room: "placeholder room"
      });

    },
    [user, userStore.createEmptyMatrixUserIdentity, matrixStore.updateMatrixUserIdentity]
  )

  return (
    <VerticalGroup>

      <HorizontalGroup>
        <Text>
          Username:
        </Text>

        <Input
          onChange={getMatrixIdentityUserIdUpdateHandler}
          placeholder={user_matrix_identity == null ? "@username@example.org" : user_matrix_identity.user_id }
        />

        <Tooltip
          placement="top"
          content="@username@example.org"
        >
          <Icon size="lg" className={cx('note-icon')} name="info-circle" style={{ color: '#1890ff' }} />
        </Tooltip>
      </HorizontalGroup>

      <HorizontalGroup>
        <Text>
          Matrix Room:
        </Text>

        <Input />

        <Tooltip
          placement="top"
          content="!room-name@example.org"
        >
          <Icon size="lg" className={cx('note-icon')} name="info-circle" style={{ color: '#1890ff' }} />
        </Tooltip>
      </HorizontalGroup>
    </VerticalGroup>
  );
});
