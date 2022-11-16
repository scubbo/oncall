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
      console.log("updated_matrix_user_id is: " + updated_matrix_user_id);
      console.log('User pk is ' + user.pk);
      console.log('User email is ' + user.email);

      const currentMatrixIdForeignKey = user.matrix_user_identity;
      console.log('Current foreign key is ' + currentMatrixIdForeignKey);

      if (currentMatrixIdForeignKey == null) {
        console.log("foreign key is null");
        const matrix_create_response = await matrixStore.createMatrixUserIdentity({
          user_id: updated_matrix_user_id,
          paging_room: "placeholder room"
        });

        console.log(matrix_create_response)
      } else {
        await matrixStore.updateMatrixUserIdentity(currentMatrixIdForeignKey, {
          user_id: updated_matrix_user_id,
          paging_room: "placeholder room"
        });
      }

//       await userStore.loadUser(userPk);
//       const updated_user_info = userStore.items[userPk];
//       console.log(updated_user_info);

    },
//     [user, matrixStore, matrixStore.createMatrixUserIdentity, matrixStore.updateMatrixUserIdentity]
    [user, matrixStore.createMatrixUserIdentity, matrixStore.updateMatrixUserIdentity]
  )

  return (
    <VerticalGroup>
{/*       <HorizontalGroup> */}
{/*         <Text> */}
{/*           {"Content of Text" + (user_matrix_identity === undefined ? "a" : "b")} */}
{/*         </Text> */}
{/*       </HorizontalGroup> */}

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
