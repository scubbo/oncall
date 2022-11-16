import React, { useCallback } from 'react';

import { Button, HorizontalGroup, Icon, Input, Tooltip, VerticalGroup } from '@grafana/ui';
import cn from 'classnames/bind';
import { observer } from 'mobx-react';

import Block from 'components/GBlock/Block';
import Text from 'components/Text/Text';
import { SlackNewIcon } from 'icons';
import { useStore } from 'state/useStore';

import styles from './MatrixTab.module.css';

const cx = cn.bind(styles);

interface MatrixInfoProps extends HTMLAttributes<HTMLElement> {
  userPk?: User['pk'];
}

export const MatrixInfo = observer((props: MatrixInfoProps) => {

  const userPk = props.userPk
  const store = useStore();
  const { userStore, teamStore } = store;

  const user = userStore.items[userPk];

  return (
    <VerticalGroup>
      <HorizontalGroup>
        <Text>
          Username:
        </Text>

        <Input />

        <!--
            TODO - Reference env variables to permit just setting `@username` and
            defaulting to using the homeserver
        -->

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
};
