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

      var matrixUserIdPrimaryKey = user.matrix_user_identity?.id;
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
      });

    },
    [user, userStore.createEmptyMatrixUserIdentity, matrixStore.updateMatrixUserIdentity]
  )

  // TODO - this has exactly the same logic, modulo subbing "paging_room_id" for "user_id".
  // Use currying to extract this to a single method.
  const getMatrixIdentityPagingRoomIdUpdateHandler = useCallback(
      async (event) => {
        const updated_paging_room_id = event.target.value;

        var matrixUserIdPrimaryKey = user.matrix_user_identity?.id;
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
          paging_room_id: updated_paging_room_id
        });

      },
      [user, userStore.createEmptyMatrixUserIdentity, matrixStore.updateMatrixUserIdentity]
    )

  return (
    <VerticalGroup>

      <HorizontalGroup>
        <Text>
          User ID:
        </Text>

        <Input
          autoFocus
          onChange={getMatrixIdentityUserIdUpdateHandler}
          placeholder={user_matrix_identity == null ? "@username:example.org" : user_matrix_identity.user_id }
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

        <Input
          onChange={getMatrixIdentityPagingRoomIdUpdateHandler}
          placeholder={user_matrix_identity == null ? "#room-alias:example.org" : user_matrix_identity.paging_room_id }
        />

        <Tooltip
          placement="top"
          content="!room-id@example.org OR #room-alias@example.org"
        >
          <Icon size="lg" className={cx('note-icon')} name="info-circle" style={{ color: '#1890ff' }} />
        </Tooltip>
      </HorizontalGroup>
    </VerticalGroup>
  );
});
