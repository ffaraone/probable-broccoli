# -*- coding: utf-8 -*-
#
# Copyright (c) 2022, Globex Corporation
# All rights reserved.
#
from typing import List

from connect.client import AsyncConnectClient, R
from connect.eaas.core.decorators import (
    account_settings_page,
    module_pages,
    router,
    web_app,
)
from connect.eaas.core.extension import WebApplicationBase
from connect.eaas.core.inject.asynchronous import get_installation, get_installation_client
from connect.eaas.core.inject.common import get_call_context
from connect.eaas.core.inject.models import Context
from fastapi import Depends

from connect_ext.schemas import Marketplace, Settings


@web_app(router)
@account_settings_page('Chart settings', '/static/settings.html')
@module_pages('Chart', '/static/index.html')
class TestAsyncWebApplication(WebApplicationBase):

    @router.get(
        '/settings',
        summary='Retrive charts settings',
        response_model=Settings,
    )
    async def retrieve_settings(
        self,
        installation: dict = Depends(get_installation),
    ):
        return Settings(marketplaces=installation['settings'].get('marketplaces', []))

    @router.post(
        '/settings',
        summary='Save charts settings',
        response_model=Settings,
    )
    async def save_settings(
        self,
        settings: Settings,
        context: Context = Depends(get_call_context),
        client: AsyncConnectClient = Depends(get_installation_client),
    ):
        await client('devops').installations[context.installation_id].update(
            payload={
                'settings': settings.dict(),
            },
        )
        return settings

    @router.get(
        '/marketplaces',
        summary='List all available marketplaces',
        response_model=List[Marketplace],
    )
    async def list_marketplaces(
        self,
        client: AsyncConnectClient = Depends(get_installation_client),
    ):
        return [
            Marketplace(**marketplace)
            async for marketplace in client.marketplaces.all().values_list(
                'id', 'name', 'description', 'icon',
            )
        ]

    @router.get(
        '/chart',
        summary='Generate chart data',
    )
    async def generate_chart_data(
        self,
        installation: dict = Depends(get_installation),
        client: AsyncConnectClient = Depends(get_installation_client),
    ):
        data = {}
        for mp in installation['settings'].get('marketplaces', []):
            active_assets = await client('subscriptions').assets.filter(
                R().marketplace.id.eq(mp['id']) & R().status.eq('active'),
            ).count()
            data[mp['id']] = active_assets

        return {
            'type': 'bar',
            'data': {
                'labels': list(data.keys()),
                'datasets': [
                    {
                        'label': 'Subscriptions',
                        'data': list(data.values()),
                    },
                ],
            },
        }
